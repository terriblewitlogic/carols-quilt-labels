import { PX_PER_MM, JEF_PER_MM, HOOPS } from './constants.js';
import { hexToJefColor } from './colors.js';

const PX2JEF = JEF_PER_MM / PX_PER_MM;

export function encodeJEF(groups, hoopKey, canvasW, canvasH) {
  const hoop = HOOPS[hoopKey] || HOOPS['5x7'];
  const threadCount = groups.length;
  const headerSize = 116;
  const colorListSize = threadCount * 4;
  const typeListSize = threadCount * 4;
  const stitchOffset = headerSize + colorListSize + typeListSize;

  const sd = [];
  let cx = 0, cy = 0, stitchCount = 0;
  let minX = 0, minY = 0, maxX = 0, maxY = 0;

  const emit = (dx, dy, jump) => {
    while (Math.abs(dx) > 0 || Math.abs(dy) > 0) {
      const sx = Math.sign(dx) * Math.min(Math.abs(dx), 127);
      const sy = Math.sign(dy) * Math.min(Math.abs(dy), 127);
      if (!sx && !sy) break;
      if (jump) { sd.push(0x80, 0x02); }
      sd.push(sx < 0 ? sx + 256 : sx, sy < 0 ? sy + 256 : sy);
      dx -= sx; dy -= sy;
      stitchCount++;
    }
  };

  for (let g = 0; g < groups.length; g++) {
    if (g > 0) sd.push(0x80, 0x01, 0x00, 0x00); // COLOR_CHANGE: 4 bytes per spec (0x80 0x01 dx dy)
    for (let i = 0; i < groups[g].stitches.length; i++) {
      const { x, y } = groups[g].stitches[i];
      const ex = Math.round((x - canvasW / 2) * PX2JEF);
      const ey = -Math.round((y - canvasH / 2) * PX2JEF);
      if (ex < minX) minX = ex; if (ex > maxX) maxX = ex;
      if (ey < minY) minY = ey; if (ey > maxY) maxY = ey;
      const dx = ex - cx, dy = ey - cy;
      emit(dx, dy, i === 0);
      cx = ex; cy = ey;
    }
  }
  sd.push(0x80, 0x10);

  const totalSize = stitchOffset + sd.length;
  const buf = new ArrayBuffer(totalSize);
  const view = new DataView(buf);
  const bytes = new Uint8Array(buf);

  view.setUint32(0, stitchOffset, true);
  view.setUint32(4, 0x14, true);

  const now = new Date();
  const ds = `${now.getFullYear()}${String(now.getMonth() + 1).padStart(2, '0')}${String(now.getDate()).padStart(2, '0')}`;
  const ts = `${String(now.getHours()).padStart(2, '0')}${String(now.getMinutes()).padStart(2, '0')}${String(now.getSeconds()).padStart(2, '0')}00`;
  for (let i = 0; i < 8; i++) bytes[8 + i] = ds.charCodeAt(i);
  for (let i = 0; i < 8; i++) bytes[16 + i] = ts.charCodeAt(i);

  view.setUint32(24, threadCount, true);
  view.setUint32(28, sd.length / 2, true); // stitch_count = total 2-byte records per spec
  view.setUint32(32, hoop.jefCode, true);

  // Extent 1: design bounding box (left, top, right, bottom from hoop center, 0.1mm units)
  // Stitch data uses Y-up; extent fields use Y-down (spec: left/top negative, right/bottom positive)
  view.setInt32(36, minX, true);   // left (most negative X)
  view.setInt32(40, -maxY, true);  // top (Y-down: negate JEF maxY → negative)
  view.setInt32(44, maxX, true);   // right (most positive X)
  view.setInt32(48, -minY, true);  // bottom (Y-down: negate JEF minY → positive)
  for (let h = 1; h < 5; h++) {
    const off = 36 + h * 16;
    view.setInt32(off, -1, true); view.setInt32(off + 4, -1, true);
    view.setInt32(off + 8, -1, true); view.setInt32(off + 12, -1, true);
  }

  for (let i = 0; i < threadCount; i++)
    view.setInt32(headerSize + i * 4, hexToJefColor(groups[i].color), true);
  for (let i = 0; i < threadCount; i++)
    view.setInt32(headerSize + colorListSize + i * 4, 13, true);

  bytes.set(sd, stitchOffset);
  return bytes;
}
