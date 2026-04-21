// Hoop presets for image embroidery mode.
// w/h in mm. These are physically larger than the label-maker hoops
// since image fills work best on 4×4 or bigger.

export const IMAGE_HOOPS = {
  '4x4':   { w: 100, h: 100, label: '4×4"  (100×100 mm)' },
  '5x7':   { w: 130, h: 180, label: '5×7"  (130×180 mm)' },
  '6x10':  { w: 150, h: 240, label: '6×10" (150×240 mm)' },
};

export const DEFAULT_IMAGE_HOOP = '4x4';
