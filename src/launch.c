/* Tile app that opens one of LG's own apps (Settings, Notifications, Search...) and exits.
 * Native app without a window, so no app screen flashes. It tries each app id
 * in TARGETS in order until webOS accepts one: the ids differ between webOS
 * versions. Build with -DTARGETS='"first.id","fallback.id"'.
 * Optional launch parameters, one JSON object per id in the same order ("" for
 * none): -DPARAMS='"{\"activateType\":\"tvguide\"}",""'. */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#ifndef TARGETS
#error "Build with -DTARGETS"
#endif
#ifndef PARAMS
#define PARAMS ""
#endif

static const char *targets[] = {TARGETS, 0};
static const char *params[] = {PARAMS};
#define NPARAMS (sizeof params / sizeof params[0])

static int launch(const char *bin, const char *id, const char *extra) {
  char cmd[1024], out[2048];
  /* Ids and params are fixed at build time (the build refuses single quotes). */
  if (snprintf(cmd, sizeof cmd,
               "%s -n 1 luna://com.webos.applicationManager/launch '{\"id\":\"%s\"%s%s}' 2>/dev/null",
               bin, id, *extra ? ",\"params\":" : "", extra) >= (int)sizeof cmd)
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
  for (size_t i = 0; targets[i]; i++)
    if (launch(bin, targets[i], i < NPARAMS ? params[i] : "")) return 0;
  return 1;
}
