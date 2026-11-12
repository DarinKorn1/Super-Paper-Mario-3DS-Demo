#include "audio.h"
#include <3ds.h>
#include <stdio.h>
#include <string.h>

// File layout (little-endian), written by tools/convert_bgm.py:
// "SBGM", u32 version, u32 rate, u32 channels (2), u32 samplesPerChannel, u32 loopStart, then interleaved s16 L R.
//
// Stereo is played as TWO MONO channels (ndsp channel 0 = left only, channel 1 = right only) because the emulator's stereo-PCM16
// path played at double speed. The track is fed in small chunks (a ring of CHUNK_BUFS buffers per channel) and the loop point is
// handled here by jumping from the end back to loopStart.
#define CHUNK_BUFS 6
#define CHUNK_SAMPLES 8192

static bool ndspUp, ok, muted;
static s16* pcm[2];                       // left, right (linear memory)
static ndspWaveBuf bufs[2][CHUNK_BUFS];
static u32 totalSamples, loopStartSample, playPos;
static u64 consumed;                 // samples the DSP has finished + position in the current buffer (for the speed read-out)
static float baseRate, rateScale = 1.0f;

bool audio_ok(void) { return ok; }
bool audio_muted(void) { return muted; }

void audio_update(void)
{
	if (!ok) return;
	for (int i = 0; i < CHUNK_BUFS; i++) {
		if (bufs[0][i].status != NDSP_WBUF_FREE && bufs[0][i].status != NDSP_WBUF_DONE)
			continue;
		if (bufs[0][i].status == NDSP_WBUF_DONE) consumed += bufs[0][i].nsamples;
		u32 n = CHUNK_SAMPLES;
		if (playPos + n > totalSamples) n = totalSamples - playPos;   // never cross the end; the next chunk starts at the loop point
		for (int c = 0; c < 2; c++) {
			ndspWaveBuf* w = &bufs[c][i];
			memset(w, 0, sizeof *w);
			w->data_vaddr = pcm[c] + playPos;
			w->nsamples = n;
			ndspChnWaveBufAdd(c, w);
		}
		playPos += n;
		if (playPos >= totalSamples) playPos = loopStartSample;
	}
}

static void free_pcm(void)
{
	for (int c = 0; c < 2; c++) { if (pcm[c]) linearFree(pcm[c]); pcm[c] = NULL; }
}

bool audio_init(const char* dir, char* err, size_t errSize)
{
	char path[256];
	snprintf(path, sizeof path, "%sbgm_flipside.pcm", dir);
	FILE* f = fopen(path, "rb");
	if (!f) { snprintf(err, errSize, "no bgm_flipside.pcm"); return false; }
	u32 hdr[6];
	if (fread(hdr, 4, 6, f) != 6 || memcmp(hdr, "SBGM", 4) != 0 || hdr[1] != 1 || hdr[3] != 2 || hdr[5] >= hdr[4]) {
		fclose(f); snprintf(err, errSize, "bad bgm file"); return false;
	}
	u32 rate = hdr[2], total = hdr[4], loopStart = hdr[5];
	size_t bytes = (size_t)total * 2;
	pcm[0] = linearAlloc(bytes);
	pcm[1] = linearAlloc(bytes);
	if (!pcm[0] || !pcm[1]) { fclose(f); free_pcm(); snprintf(err, errSize, "no memory for music (%lu KB)", (unsigned long)(bytes >> 9)); return false; }

	// read in pieces and split the interleaved L R samples
	static s16 tmp[8192 * 2];
	for (u32 done = 0; done < total; ) {
		u32 n = total - done < 8192 ? total - done : 8192;
		if (fread(tmp, 4, n, f) != n) { fclose(f); free_pcm(); snprintf(err, errSize, "bgm file truncated"); return false; }
		for (u32 i = 0; i < n; i++) { pcm[0][done + i] = tmp[2 * i]; pcm[1][done + i] = tmp[2 * i + 1]; }
		done += n;
	}
	fclose(f);

	Result rc = ndspInit();         // fails without sdmc:/3ds/dspfirm.cdc
	if (R_FAILED(rc)) {
		free_pcm();
		snprintf(err, errSize, "ndspInit failed (%08lX): dspfirm.cdc?", (unsigned long)rc);
		return false;
	}
	ndspUp = true;
	DSP_FlushDataCache(pcm[0], bytes);
	DSP_FlushDataCache(pcm[1], bytes);
	ndspSetOutputMode(NDSP_OUTPUT_STEREO);
	for (int c = 0; c < 2; c++) {
		ndspChnReset(c);
		ndspChnSetInterp(c, NDSP_INTERP_LINEAR);
		ndspChnSetRate(c, (float)rate);
		ndspChnSetFormat(c, NDSP_FORMAT_MONO_PCM16);
		float mix[12] = { 0 };
		mix[c] = 0.8f;                  // mono source: [0] = left, [1] = right
		ndspChnSetMix(c, mix);
		ndspChnSetPaused(c, true);      // start both together once queued
	}
	baseRate = (float)rate;
	// Optional sdmc:/3ds/spm3ds-demo/bgm_rate.txt: a playback-rate factor (e.g. 0.5). Needed only for Azahar, which played the music at
	// twice the speed; on a real console leave the file out (factor 1.0 = the file's own rate).
	snprintf(path, sizeof path, "%sbgm_rate.txt", dir);
	FILE* rf = fopen(path, "r");
	if (rf) {
		float r = 1.0f;
		if (fscanf(rf, "%f", &r) == 1 && r >= 0.2f && r <= 2.0f) rateScale = r;
		fclose(rf);
	}
	for (int c = 0; c < 2; c++) ndspChnSetRate(c, baseRate * rateScale);
	totalSamples = total; loopStartSample = loopStart; playPos = 0;
	memset(bufs, 0, sizeof bufs);
	ok = true;
	audio_update();
	for (int c = 0; c < 2; c++) ndspChnSetPaused(c, false);
	return true;
}

void audio_toggle_mute(void)
{
	if (!ok) return;
	muted = !muted;
	for (int c = 0; c < 2; c++) ndspChnSetPaused(c, muted);
}

void audio_exit(void)
{
	if (ndspUp) {
		for (int c = 0; c < 2; c++) ndspChnReset(c);
		ndspExit();
	}
	free_pcm();
	ndspUp = ok = false;
}

// Debug: total samples played so far (finished buffers + position inside the playing one).
u64 audio_samples_played(void)
{
	if (!ok) return 0;
	return consumed + ndspChnGetSamplePos(0);
}

float audio_rate_scale(void) { return rateScale; }

// Debug: scale the playback rate (1.0 = file rate). Only for finding out what an emulator does; leave at 1.0 on hardware.
void audio_adjust_rate(float factor)
{
	if (!ok) return;
	rateScale *= factor;
	if (rateScale < 0.2f) rateScale = 0.2f;
	if (rateScale > 2.0f) rateScale = 2.0f;
	for (int c = 0; c < 2; c++) ndspChnSetRate(c, baseRate * rateScale);
}
