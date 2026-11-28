#!/bin/sh
# Smoke test of the running site: asks it what a browser would ask for and exits 0 if every check
# passes, 1 if any fails. One line per check (PASS or FAIL), then "N/M checks passed".
#
# POSIX sh and wget only, so the same file runs in two places:
#   - in the production image (busybox wget), from the smoke CronJob in tnoff/docker-apps, against the
#     in-cluster Service. That path skips DNS, TLS and the ingress.
#   - on a GitHub runner (GNU wget), from .github/workflows/smoke-public.yml, against the public url.
#     That path walks all of it.
#
# SMOKE_BASE_URL  no trailing slash, e.g. https://tyler-north.com or http://website-svc.personal-website.svc.cluster.local:8080
# SMOKE_TRIES     attempts per request (default 3), so one dropped connection does not fail the run
# SMOKE_TIMEOUT   seconds per attempt (default 15)
#
# Never builds a client or reads a secret: the site has no auth and this holds no credentials.

BASE="${SMOKE_BASE_URL:-}"
TRIES="${SMOKE_TRIES:-3}"
TIMEOUT="${SMOKE_TIMEOUT:-15}"

if [ -z "$BASE" ]; then
    echo "SMOKE_BASE_URL is not set" >&2
    exit 2
fi
BASE="${BASE%/}"

TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"' EXIT INT TERM

PASSED=0
TOTAL=0

pass() { PASSED=$((PASSED + 1)); TOTAL=$((TOTAL + 1)); echo "PASS $1"; }
fail() { TOTAL=$((TOTAL + 1)); echo "FAIL $1"; }

# fetch PATH: leaves the final status in $STATUS, the response headers in $TMP/headers and the body in
# $TMP/body. wget exits non-zero on a 4xx/5xx but -S still prints the headers, so the status comes from
# those, not the exit code. After a redirect the headers hold several status lines: the last one counts.
fetch() {
    STATUS=""
    : > "$TMP/headers"
    : > "$TMP/body"
    n=0
    while [ "$n" -lt "$TRIES" ]; do
        n=$((n + 1))
        wget -S -T "$TIMEOUT" -t 1 -O "$TMP/body" "$BASE$1" 2> "$TMP/headers" || true
        STATUS="$(sed -n 's/^ *HTTP\/[0-9.]* \([0-9][0-9][0-9]\).*/\1/p' "$TMP/headers" | tail -n 1)"
        # No status means no response (refused, reset, timed out): that is worth another try. Any
        # status, even a 404, is an answer and is not retried.
        [ -n "$STATUS" ] && return 0
        sleep 1
    done
    return 0
}

header() {
    # header NAME (lower case): the last value of a response header, whitespace trimmed. Header names
    # are case-insensitive and servers differ, so the whole file is lower-cased before matching; sed's
    # I flag is not used because busybox sed does not have it.
    tr '[:upper:]' '[:lower:]' < "$TMP/headers" | sed -n "s/^ *$1: *//p" | tail -n 1 | tr -d '\r'
}

check_status() {
    # check_status NAME PATH WANT
    fetch "$2"
    if [ "$STATUS" = "$3" ]; then
        pass "$1: $3 for $2"
    else
        fail "$1: status ${STATUS:-none (no response)} for $2, expected $3"
    fi
}

# /_health/ is what the kubelet probes; if this fails nothing else is worth reading.
fetch /_health/
if [ "$STATUS" = "200" ] && grep -q '^OK' "$TMP/body"; then
    pass "health: 200 OK"
else
    fail "health: status ${STATUS:-none (no response)}, body not OK"
fi

fetch /
if [ "$STATUS" = "200" ] && grep -q 'Tyler North' "$TMP/body"; then
    pass "homepage: 200 with the site's content"
else
    fail "homepage: status ${STATUS:-none (no response)} or content missing"
fi

if [ "$STATUS" = "200" ]; then
    case "$(header x-content-type-options)" in
        nosniff) pass "headers: X-Content-Type-Options nosniff on the homepage" ;;
        *) fail "headers: X-Content-Type-Options missing from the homepage" ;;
    esac
else
    fail "headers: needs the homepage check, which did not pass"
fi

# With the trailing slash on purpose. Without it nginx answers 301 to http://tyler-north.com/resume/
# (port_in_redirect off, and it sees plain http behind the ingress), which names the public host: a
# pod cannot reach that (see the smoke CronJob in docker-apps), and busybox wget does not follow the
# 308 the ingress then sends. The site's own nav links omit the slash and work in a browser.
check_status "resume" /resume/ 200
check_status "projects" /projects/ 200
check_status "stylesheet" /css/bootstrap.min.css 200

# The resume PDF is generated and copied into the image by hand-run tooling, so it is the file most
# likely to go missing or turn into an HTML error page that still answers 200.
fetch /Tyler_Daniel_North_CV.pdf
if [ "$STATUS" = "200" ] && [ "$(head -c 4 "$TMP/body")" = "%PDF" ] && [ "$(wc -c < "$TMP/body")" -gt 10000 ]; then
    pass "resume pdf: 200, a PDF, over 10 KB"
else
    fail "resume pdf: status ${STATUS:-none (no response)}, or not a PDF over 10 KB"
fi

# A path that does not exist must 404. A catch-all that answers 200 would hide every broken link.
check_status "missing page" /smoke-no-such-page 404

echo "${PASSED}/${TOTAL} checks passed"
[ "$PASSED" -eq "$TOTAL" ]
