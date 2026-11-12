#include "audio.h"
#include <3ds.h>
#include <stdio.h>
#include <string.h>

// File layout (little-endian), written by tools/convert_bgm.py:
// "SBGM", u32 version, u32 rate, u32 channels, u32 samplesPerChannel, u32 loopStart, then interleaved s16.
static bool ndspUp, ok, muted;
static void* pcm;
// The track is fed to the DSP in small chunks (a ring of CHUNK_BUFS buffers of CHUNK_SAMPLES) instead of one 2-million-sample buffer:
// emulators (and the DSP) handle small buffers better, and the loop point is handled here by jumping from the end back to loopStart.
#define CHUNK_BUFS 6
#define CHUNK_SAMPLES 8192
static ndspWaveBuf bufs[CHUNK_BUFS];
static u32 totalSamples, loopStartSample, playPos;

bool audio_ok(void) { return ok; }
bool audio_muted(void) { return muted; }

void audio_update(void)
{
	if (!ok) return;
	for (int i = 0; i < CHUNK_BUFS; i++) {
		ndspWaveBuf* w = &bufs[i];
		if (w->status != NDSP_WBUF_FREE && w->status != NDSP_WBUF_DONE)
			continue;
		u32 n = CHUNK_SAMPLES;
		if (playPos + n > totalSamples) n = totalSamples - playPos;   // never cross the end; the next chunk starts at the loop point
		memset(w, 0, sizeof *w);
		w->data_vaddr = (const s16*)pcm + (size_t)playPos * 2;
		w->nsamples = n;
		ndspChnWaveBufAdd(0, w);
		playPos += n;
		if (playPos >= totalSamples) playPos = loopStartSample;
	}
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
	size_t bytes = (size_t)total * 4;
	pcm = linearAlloc(bytes);      // ndsp reads wave buffers from linear memory
	if (!pcm) { fclose(f); snprintf(err, errSize, "no memory for music (%lu KB)", (unsigned long)(bytes >> 10)); return false; }
	size_t got = fread(pcm, 1, bytes, f);
	fclose(f);
	if (got != bytes) { linearFree(pcm); pcm = NULL; snprintf(err, errSize, "bgm file truncated"); return false; }

	Result rc = ndspInit();         // fails without the DSP firmware (sdmc:/3ds/dspfirm.cdc on a real console)
	if (R_FAILED(rc)) {
		linearFree(pcm); pcm = NULL;
		snprintf(err, errSize, "ndspInit failed (%08lX): dspfirm.cdc?", (unsigned long)rc);
		return false;
	}
	ndspUp = true;
	DSP_FlushDataCache(pcm, bytes);
	ndspSetOutputMode(NDSP_OUTPUT_STEREO);
	ndspChnReset(0);
	ndspChnSetInterp(0, NDSP_INTERP_LINEAR);
	ndspChnSetRate(0, (float)rate);
	ndspChnSetFormat(0, NDSP_FORMAT_STEREO_PCM16);
	float mix[12] = { 0.8f, 0.8f };
	ndspChnSetMix(0, mix);

	totalSamples = total; loopStartSample = loopStart; playPos = 0;
	memset(bufs, 0, sizeof bufs);
	ok = true;
	audio_update();
	return true;
}

void audio_toggle_mute(void)
{
	if (!ok) return;
	muted = !muted;
	ndspChnSetPaused(0, muted);
}

void audio_exit(void)
{
	if (ndspUp) {
		ndspChnReset(0);
		ndspExit();
	}
	if (pcm) linearFree(pcm);
	pcm = NULL; ndspUp = ok = false;
}
