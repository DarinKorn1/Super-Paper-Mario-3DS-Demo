// Background music through ndsp (libctru's DSP audio): Flipside theme, 16-bit stereo PCM held in RAM, intro + looped part.
#pragma once
#include <stdbool.h>
#include <stddef.h>

bool audio_init(const char* dir, char* err, size_t errSize);   // loads bgm_flipside.pcm (tools/convert_bgm.py) and starts it
void audio_exit(void);
bool audio_ok(void);
void audio_toggle_mute(void);
bool audio_muted(void);
void audio_update(void);   // call once per frame: refills the DSP buffers
unsigned long long audio_samples_played(void);   // debug: samples consumed by the DSP so far (per channel)
float audio_rate_scale(void);
void audio_adjust_rate(float factor);
