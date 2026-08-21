#!/usr/bin/env bash
# DEPRECATED — this is a wrapper, kept so a published reference does not dangle.
#
# Fifteen course roadmaps wired this script as their CI conformance gate and as
# a milestone acceptance criterion. It could never do that job: it hard-codes
# its own repo root and globs THIS repo's levels/*.md, with no --manifest flag
# and no way to be pointed at a course. Run from a course it audited the
# framework's own 1,170 statements, printed OK and exited 0 — regardless of
# what the course contained. Every one of those gates passed vacuously.
#
# Those roadmaps have been corrected. This wrapper exists for anything else
# still calling the old name.
#
#   framework self-check :  conformance_audit.py self-audit   (what this does)
#   course conformance   :  conformance_audit.py resolve --manifest ... --content ...
set -euo pipefail
here="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
echo "id-audit.sh is deprecated; running 'conformance_audit.py self-audit'." >&2
echo "A COURSE must use 'resolve --manifest', which this script cannot do." >&2
exec python3 "$here/conformance_audit.py" self-audit "$@"
