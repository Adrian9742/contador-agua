from PIL import Image
from pathlib import Path

src = Path(__file__).parent / "icon_source.png"
dst = Path(__file__).parent / "icon.ico"

img = Image.open(src).convert("RGBA")

sizes = [256, 64, 48, 32, 16]
imgs  = [img.resize((s, s), Image.LANCZOS) for s in sizes]

imgs[0].save(dst, format="ICO", sizes=[(s, s) for s in sizes],
             append_images=imgs[1:])

print(f"Salvo: {dst}  ({dst.stat().st_size // 1024} KB)")
print(f"Tamanhos: {sizes}")
