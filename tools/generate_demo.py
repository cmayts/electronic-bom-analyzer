"""Generate privacy-safe README visuals from synthetic output."""

from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


WIDTH, HEIGHT = 1120, 620
BG = "#0b1220"
PANEL = "#111c2e"
INK = "#e6edf7"
MUTED = "#93a4bc"
GREEN = "#59d499"
YELLOW = "#f5c451"
RED = "#ff7b72"


def font(size: int, bold: bool = False):
    candidates = [
        Path("C:/Windows/Fonts/consolab.ttf" if bold else "C:/Windows/Fonts/consola.ttf"),
        Path("/usr/share/fonts/truetype/dejavu/DejaVuSansMono-Bold.ttf" if bold else "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf"),
    ]
    for candidate in candidates:
        if candidate.exists():
            return ImageFont.truetype(str(candidate), size)
    return ImageFont.load_default()


def frame(lines: list[tuple[str, str]]) -> Image.Image:
    image = Image.new("RGB", (WIDTH, HEIGHT), BG)
    draw = ImageDraw.Draw(image)
    draw.rounded_rectangle((35, 35, WIDTH - 35, HEIGHT - 35), 18, fill=PANEL, outline="#26364f", width=2)
    draw.ellipse((65, 62, 83, 80), fill=RED)
    draw.ellipse((95, 62, 113, 80), fill=YELLOW)
    draw.ellipse((125, 62, 143, 80), fill=GREEN)
    draw.text((170, 58), "electronic-bom-analyzer", font=font(22, True), fill=INK)
    y = 115
    for text, color in lines:
        draw.text((70, y), text, font=font(22), fill=color)
        y += 46
    return image


def main() -> None:
    command = [("$ python -m bom_analyzer examples/synthetic_bom.csv --output results", GREEN)]
    output = [
        ("Rows read: 5", INK),
        ("Unique components: 4", INK),
        ("Errors: 1", RED),
        ("Warnings: 2", YELLOW),
        ("Report: results/bom_report.json", MUTED),
        ("Normalized BOM: results/normalized_bom.csv", MUTED),
        ("HTML report: results/bom_report.html", MUTED),
    ]
    frames = [frame(command + output[:count]) for count in range(len(output) + 1)]
    docs = Path("docs")
    docs.mkdir(exist_ok=True)
    frames[-1].save(docs / "report-preview.png")
    frames[0].save(docs / "demo.gif", save_all=True, append_images=frames[1:], duration=450, loop=0)


if __name__ == "__main__":
    main()
