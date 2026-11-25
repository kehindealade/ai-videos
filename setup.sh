#!/usr/bin/env bash
set -e

if command -v apt-get >/dev/null 2>&1; then
  sudo apt-get update -y || apt-get update -y
  (sudo apt-get install -y ffmpeg libcairo2-dev pkg-config fonts-dejavu fonts-liberation fontconfig || apt-get install -y ffmpeg libcairo2-dev pkg-config fonts-dejavu fonts-liberation fontconfig)
fi

PIP="pip install"
python3 -m pip install --help 2>/dev/null | grep -q break-system-packages && PIP="pip install --break-system-packages"
$PIP pycairo numpy scipy soundfile Pillow librosa kokoro-onnx
if [ "${WITH_CHATTERBOX:-0}" = "1" ]; then
  $PIP torch --index-url https://download.pytorch.org/whl/cpu
  $PIP chatterbox-tts
  echo "Chatterbox installed. Apply the two float32 patches in claude/money-map-ram-engine/README.txt."
fi

FONTS="$HOME/.fonts"
mkdir -p "$FONTS"
G=https://raw.githubusercontent.com/google/fonts/main
fetch() { [ -f "$FONTS/$(basename "$1")" ] || curl -fsSL "$G/$1" -o "$FONTS/$(basename "$1")" || echo "font missing: $1"; }
for w in ExtraBold Bold Medium; do
  fetch ofl/roundedmplus1c/RoundedMplus1c-$w.ttf
  fetch ofl/mplusrounded1c/MPLUSRounded1c-$w.ttf
done
fetch ofl/lilitaone/LilitaOne-Regular.ttf
fetch apache/luckiestguy/LuckiestGuy-Regular.ttf
fetch ofl/sharetechmono/ShareTechMono-Regular.ttf
fetch ofl/architectsdaughter/ArchitectsDaughter-Regular.ttf
fetch ofl/anton/Anton-Regular.ttf
fetch ofl/archivoblack/ArchivoBlack-Regular.ttf
fetch ofl/anonymouspro/AnonymousPro-Regular.ttf
fetch ofl/anonymouspro/AnonymousPro-Bold.ttf
for w in Regular Medium SemiBold Bold ExtraBold Black; do fetch ofl/poppins/Poppins-$w.ttf; done
fetch ofl/inter/Inter%5Bopsz,wght%5D.ttf
fetch ofl/dmsans/DMSans%5Bopsz,wght%5D.ttf
fetch ofl/gelasio/Gelasio%5Bwght%5D.ttf
fetch ofl/cardo/Cardo-Regular.ttf
fetch ofl/cardo/Cardo-Bold.ttf
fetch ofl/montserrat/Montserrat%5Bwght%5D.ttf
fetch ofl/bitter/Bitter%5Bwght%5D.ttf
fetch ofl/opensans/OpenSans%5Bwdth,wght%5D.ttf
fetch ofl/firasans/FiraSans-Regular.ttf
fetch ofl/firasans/FiraSans-Bold.ttf
fetch ofl/firasans/FiraSans-Black.ttf
fetch ofl/roboto/Roboto%5Bwdth,wght%5D.ttf
fetch ofl/lora/Lora%5Bwght%5D.ttf
fetch ofl/barlowcondensed/BarlowCondensed-Bold.ttf
fetch ofl/barlow/Barlow-Regular.ttf
fetch ofl/permanentmarker/PermanentMarker-Regular.ttf
fetch ofl/kalam/Kalam-Regular.ttf
fetch ofl/cormorantsc/CormorantSC-Bold.ttf
fetch ofl/ibmplexserif/IBMPlexSerif-Bold.ttf
fetch ofl/sairaextracondensed/SairaExtraCondensed-Bold.ttf
fc-cache -f >/dev/null 2>&1 || true

K=/root/kokoro
[ -w /root ] || K="$HOME/kokoro"
mkdir -p "$K"
R=https://github.com/thewh1teagle/kokoro-onnx/releases/download/model-files-v1.0
[ -f "$K/kokoro-v1.0.onnx" ] || curl -fsSL "$R/kokoro-v1.0.onnx" -o "$K/kokoro-v1.0.onnx"
[ -f "$K/voices-v1.0.bin" ] || curl -fsSL "$R/voices-v1.0.bin" -o "$K/voices-v1.0.bin"
[ "$K" = /root/kokoro ] || echo "Kokoro files are in $K. Engines expect /root/kokoro: symlink it or edit the path in tts.py."

echo "Setup done. Some engines name extra fonts in their README; fetch those from $G the same way."
