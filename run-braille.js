import { ImageData } from "canvas";
global.ImageData = ImageData;

import { convertImageToBraille } from "./dist/braille-node.js";

const args = process.argv.slice(2);

const path = args[0];
const width = parseInt(args[1]) || 100;
const dither = args[2] || "floydSteinberg";
const threshold = parseInt(args[3]) || 127;
const invert = args[4] === "true";

convertImageToBraille(path, {
    width,
    dither,
    threshold,
    invert
}).then(result => {
    console.log(result);
});
