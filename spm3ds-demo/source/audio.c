#include "audio.h"
#include <3ds.h>
#include <stdio.h>
#include <string.h>

// File layout (little-endian), written by tools/convert_bgm.py:
// "SBGM", u32 version, u32 rate, u32 channels, u32 samplesPerChannel, u32 loopStart, then interleaved s16.
static bool ndspUp, ok, muted;
static void* pcm;
static ndspWaveBuf intro, loopBuf;

bool audio_ok(void) { return ok; }
bool audio_muted(void) { return muted; }

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

	// Intro (start of the track up to the loop point), then the loop body repeated forever.
	memset(&intro, 0, sizeof intro);
	memset(&loopBuf, 0, sizeof loopBuf);
	intro.data_vaddr = pcm;
	intro.nsamples = loopStart;
	loopBuf.data_vaddr = (const s16*)pcm + (size_t)loopStart * 2;
	loopBuf.nsamples = total - loopStart;
	loopBuf.looping = true;
	ndspChnWaveBufAdd(0, &intro);
	ndspChnWaveBufAdd(0, &loopBuf);
	ok = true;
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
