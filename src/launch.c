/* Tile app that opens one of LG's own panels (Settings, Notifications) and exits.
 * Native app without a window, so no app screen flashes. It tries each app id
 * in TARGETS in order until webOS accepts one: the ids differ between webOS
 * versions. Build with -DTARGETS='"first.id","fallback.id"'. */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#ifndef TARGETS
#error "Build with -DTARGETS"
#endif

static const char *targets[] = {TARGETS, 0};

static int launch(const char *bin, const char *id) {
  char cmd[512], out[2048];
  /* App ids are fixed at build time; quote them anyway. */
  if (snprintf(cmd, sizeof cmd,
               "%s -n 1 luna://com.webos.applicationManager/launch '{\"id\":\"%s\"}' 2>/dev/null",
               bin, id) >= (int)sizeof cmd)
    return 0;
  FILE *p = popen(cmd, "r");
  if (!p) return 0;
  size_t n = fread(out, 1, sizeof out - 1, p);
  out[n] = 0;
  pclose(p);
  return strstr(out, "\"returnValue\":true") || strstr(out, "\"returnValue\": true");
}

int main(void) {
  /* Overridable only for host tests; on the TV the public bus client is used. */
  const char *bin = getenv("SHORTCUT_LUNA_SEND");
  if (!bin || !*bin) bin = "/usr/bin/luna-send-pub";
  for (int i = 0; targets[i]; i++)
    if (launch(bin, targets[i])) return 0;
  return 1;
}
