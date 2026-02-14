import { createCanvas, loadImage } from "canvas";
import KernelDitherer from "./kernel-ditherer.js";
import { rgbaOffset } from "./helpers.js";

const asciiXDots = 2;
const asciiYDots = 4;

const ditherers = {
    threshold: new KernelDitherer([0, 0], [], 1),
    floydSteinberg: new KernelDitherer([1, 0], [
        [0, 0, 7],
        [3, 5, 1],
    ], 16),
    stucki: new KernelDitherer([2, 0], [
        [0, 0, 0, 8, 4],
        [2, 4, 8, 4, 2],
        [1, 2, 4, 2, 1],
    ], 42),
    atkinson: new KernelDitherer([1, 0], [
        [0, 0, 1, 1],
        [1, 1, 1, 0],
        [0, 1, 0, 0],
    ], 8),
};

export async function convertImageToBraille(path, {
    width = 100,
    dither = "floydSteinberg",
    threshold = 127,
    invert = false
} = {}) {

    const image = await loadImage(path);

    const asciiHeight = Math.ceil(width * asciiXDots * (image.height / image.width) / asciiYDots);

    const canvas = createCanvas(width * asciiXDots, asciiHeight * asciiYDots);
    const context = canvas.getContext("2d");

    context.fillStyle = "white";
    context.fillRect(0, 0, canvas.width, canvas.height);

    context.globalCompositeOperation = "luminosity";
    context.drawImage(image, 0, 0, canvas.width, canvas.height);

    const ditherer = ditherers[dither];
    const greyPixels = context.getImageData(0, 0, canvas.width, canvas.height);
    const ditheredPixels = ditherer.dither(greyPixels, threshold);

    const targetValue = invert ? 255 : 0;

    let asciiLines = [];

    for (let y = 0; y < canvas.height; y += asciiYDots) {
        const line = [];
        for (let x = 0; x < canvas.width; x += asciiXDots) {
            const braille =
                10240
                + ((ditheredPixels.data[rgbaOffset(x + 1, y + 3, canvas.width)] === targetValue) << 7)
                + ((ditheredPixels.data[rgbaOffset(x + 0, y + 3, canvas.width)] === targetValue) << 6)
                + ((ditheredPixels.data[rgbaOffset(x + 1, y + 2, canvas.width)] === targetValue) << 5)
                + ((ditheredPixels.data[rgbaOffset(x + 1, y + 1, canvas.width)] === targetValue) << 4)
                + ((ditheredPixels.data[rgbaOffset(x + 1, y + 0, canvas.width)] === targetValue) << 3)
                + ((ditheredPixels.data[rgbaOffset(x + 0, y + 2, canvas.width)] === targetValue) << 2)
                + ((ditheredPixels.data[rgbaOffset(x + 0, y + 1, canvas.width)] === targetValue) << 1)
                + ((ditheredPixels.data[rgbaOffset(x + 0, y + 0, canvas.width)] === targetValue) << 0);

            line.push(String.fromCharCode(braille));
        }
        asciiLines.push(line.join(""));
    }

    return asciiLines.join("\n");
}
