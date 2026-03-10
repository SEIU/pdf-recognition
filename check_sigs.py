import io
from os.path import basename

import numpy as np
from PIL import Image, ImageChops
from pypdf import PdfReader

default_density_threshold = 5


def trim(
    img: Image.Image,
) -> Image.Image:
    bg = Image.new("RGB", img.size, img.getpixel((0, 0)))
    diff = ImageChops.difference(img.convert("RGB"), bg)
    diff = ImageChops.add(diff, diff, 2.0, -100)
    bbox = diff.getbbox()
    if bbox:
        img = img.crop(bbox)
    return img


def report(fname: str, cfg: dict) -> None:
    """
    Analyze a PDF file and report on the presence and density of signatures.
    """
    # Check the configuration dict
    if "signatures" not in cfg:
        raise ValueError(
            "`signature` key indicating regions is missing from the config file"
        )
    regions = cfg["signatures"]
    density_threshold = cfg.get("density_threshold", default_density_threshold)

    reader = PdfReader(fname)
    page = reader.pages[0]
    try:
        # The real page is typically in index 1
        data = page.images[1].data
    except IndexError:
        # But sometimes there is only index 0
        data = page.images[0].data

    img = Image.open(io.BytesIO(data))
    if cfg.get("trim", False):
        img = trim(img)

    first, last, date = parse_filename(fname)

    # Config has region as percentages, convert to pixel offsets
    for name, (_left, _upper, _right, _lower) in regions.items():  # type: ignore
        width, height = img.size
        left = _left * width
        upper = _upper * height
        right = _right * width
        lower = _lower * height

        sig = find_signature(img, (left, upper, right, lower))
        # Some signatories do not use full box, look for top half and bottom half
        sections = signature_sections(sig)
        density = max(*[section.mean() for section in sections])
        _fn = basename(fname)
        source = ":".join(fname.split("/")[2:4])
        if density > density_threshold:
            print(f"{first}|{last}|{date}|{source}|{name}|Y|{density:0.1f}")
        else:
            print(f"{first}|{last}|{date}|{source}|{name}|N|{density:0.1f}")


def find_outline(arr: np.ndarray) -> np.ndarray:
    """
    Identify a box around a signature.

    Boxes are assumed to be drawn with approximately grayscale 44.

    Other lines of text may be darker on average, but their
    variance between black and white pixels will be much higher
    """
    row_means = arr.mean(axis=1)
    row_vars = arr.var(axis=1)
    top_line, bottom_line = 0, arr.shape[0]
    found_top = False
    many = 1_000  # Number or rows larger than we ever consider
    for n, mean, var in zip(range(many), row_means, row_vars):
        if mean > 25 and var < 250:
            if not found_top:
                top_line = n
            else:
                bottom_line = n
                break
        elif top_line > 0:
            found_top = True
    
    if found_top:
        arr = arr[top_line + 1 : bottom_line]
    else:
        # Found no outline, return array of zeros (black; no signature)
        arr[:,:] = 0
    return arr


def find_signature(img, region: tuple[float, float, float, float]) -> np.ndarray:
    # The signature position is not completely fixed, but SHOULD BE
    # bounded by an outline of approximately pixel value 44
    img = img.convert("L")
    img = ImageChops.invert(img)
    sig = img.crop(region)
    arr = np.array(sig)
    arr = find_outline(arr)
    return arr


def parse_filename(fname: str) -> tuple[str, str, str]:
    "Extract firstname, lastname, and date from scan filename"
    date_at = fname.rfind("202")  # ISO 8601 202N-NN-NN
    date = fname[date_at : date_at + 10]
    name = fname[: date_at - 1].split("/")[-1]
    # There are sometimes dots inside name components :-(
    parts = name.split(".")
    first = parts[0]
    last = parts[-1]
    return first, last, date


def signature_sections(sig):
    nRows, nCols = sig.shape

    top_half = sig[: nRows // 2]
    bottom_half = sig[nRows // 2 :]
    middle_vert = sig[nRows // 4 : 3 * nRows // 4]
    left_third = sig[:, 0 : nCols // 3]
    middle_horiz = sig[:, nCols // 3 : 2 * nCols // 3]
    right_third = sig[:, 2 : nCols // 3 :]
    return top_half, bottom_half, middle_vert, left_third, middle_horiz, right_third
