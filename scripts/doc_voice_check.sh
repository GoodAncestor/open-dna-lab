#!/usr/bin/env bash
# doc_voice_check.sh — house-style checks over everything that becomes page text.
#
#   ./scripts/doc_voice_check.sh
#
# Two sections, and the difference between them is the whole design:
#
#   BREAKAGE (fails the build)  — markup that corrupts the rendered page.
#                                 Objective. No taste involved. A machine can
#                                 decide it and be right every time.
#
#   ADVISORY (never fails)      — phrases and headings the house style tends to
#                                 dislike. A grep cannot tell a rhetorical
#                                 question from a real either/or, or a factual
#                                 negative from not-X-but-Y framing. It guesses,
#                                 and it is often wrong, so it does not get a
#                                 vote on whether the site builds.
#
# This used to fail the build on the advisory list. It blocked a correct
# heading — "Use a vendor, or sequence it yourself?", a genuine decision the
# page answers with a cost table — which is exactly the call a grep has no
# standing to make. Prose disagreements are settled by the writer.
#
# WHAT THIS DOES NOT CATCH: the two rules the style actually rests on —
#   1. Plain English first, then the science.
#   2. State facts; let them carry the weight.
# No grep tests those. A clean run here is a spellcheck passing, not a voice
# check passing. Read the prose.

set -uo pipefail
cd "$(dirname "$0")/.."

# Everything that becomes page text: hand-written markdown, the register prose
# fields, and the section leads baked into the generator.
TARGETS=(site/*.md data/*.yaml scripts/gen_pages.py)

fail=0

# ---------------------------------------------------------------- breakage --
# build_site.py rewrites ~x~ to <sub>x</sub>, so a *pair* of tildes on one line
# silently swallows the text between them. A lone tilde renders fine, which is
# why "~/.cache/foo" in a path is not a problem and is not flagged.
echo "==> BREAKAGE: paired tildes render as subscript"
hits=$(grep -rnE '~[^~]+~' site/*.md data/*.yaml 2>/dev/null || true)
if [ -n "$hits" ]; then
  echo "$hits" | sed 's/^/  /' | cut -c1-110
  echo "    FAIL: the text between the tildes will vanish into a <sub> span."
  echo "          Write 'about', or use the Unicode almost-equal sign."
  fail=1
else
  echo "    clean"
fi

# ---------------------------------------------------------------- advisory --
# Reviewed exceptions: substantive negatives rather than rhetorical not-X-but-Y
# framing, which the style permits. Matched against the whole source line, so
# the pattern is the readable sentence and not the fragment the grep hit.
ALLOW='Not a replacement for the OpenFlexure'
ALLOW+='|This is not a diagnostic service'

BANNED="honest|it's not |not a [A-Z]|not an arbitrary|the point is"
BANNED+="|worth (noting|being explicit)|in other words|crucially|importantly,"
BANNED+="|notably,|the beauty|state-of-the-art|by design|division of labor"
BANNED+="|neither half|is the point|makes it (ideal|clear)|the case rests"

advisory=""

# Full lines, not -o fragments: a reader needs the sentence to tell a
# rhetorical construction from a factual negative, and ALLOW needs it too.
phrases=$(grep -rniE "$BANNED" "${TARGETS[@]}" 2>/dev/null | grep -vE "$ALLOW" || true)
[ -n "$phrases" ] && advisory+="$phrases"$'\n'

# A question heading is sometimes filler and sometimes a real decision the page
# goes on to answer. Only the writer knows which.
questions=$(grep -rnE '^sub:.*\?$|^#{2,4} .*\?$' site/*.md 2>/dev/null || true)
[ -n "$questions" ] && advisory+="$questions"$'\n'

echo
echo "==> ADVISORY: house-style tells (does not fail the build)"
if [ -n "$advisory" ]; then
  printf '%s' "$advisory" | sed 's/^/  /' | cut -c1-120
  echo "    Judgement call. Rewrite if the grep is right, ignore it if not."
else
  echo "    clean"
fi

echo
if [ "$fail" -ne 0 ]; then
  echo "DOC VOICE CHECK FAILED — rendering breakage above."
  exit 1
fi
echo "DOC VOICE CHECK PASSED — nothing that breaks the page. Still read the prose."
