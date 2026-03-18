// ─── JEF Internal Palette (Janome thread codes 1–78) ────────────────────────
export const JEF_PALETTE = [
  [1,0,0,0],[2,0,0,0],[3,255,255,255],[4,255,255,23],[5,250,160,96],
  [6,92,118,73],[7,64,192,48],[8,101,194,200],[9,172,128,190],[10,245,188,203],
  [11,255,0,0],[12,192,128,0],[13,0,0,240],[14,228,195,93],[15,165,42,42],
  [16,213,176,212],[17,252,242,148],[18,240,208,192],[19,255,192,0],[20,201,164,128],
  [21,155,61,75],[22,160,184,204],[23,127,194,28],[24,229,197,202],[25,77,65,107],
  [26,0,0,0],[27,238,146,148],[28,167,79,47],[29,255,249,227],[30,0,73,134],
  [31,172,98,166],[32,173,183,151],[33,0,0,0],[34,65,130,153],[35,0,0,0],
  [36,14,8,100],[37,0,0,0],[38,140,198,211],[39,225,196,132],[40,255,123,178],
  [41,0,0,0],[42,255,0,0],[43,209,92,0],[44,0,128,0],[45,113,81,56],
  [46,240,220,80],[47,255,127,80],[48,255,255,23],[49,0,128,192],[50,0,0,128],
  [51,204,0,255],[52,255,128,200],[53,0,128,0],[54,255,165,65],[55,128,48,48],
  [56,0,35,85],[57,192,255,255],[58,138,174,128],[59,250,210,170],[60,127,127,127],
  [61,64,0,96],[62,255,64,64],[63,0,180,0],[64,255,200,0],[65,240,128,32],
  [66,176,24,112],[67,120,140,160],[68,96,96,48],[69,32,32,32],[70,228,196,148],
  [71,255,80,128],[72,0,200,200],[73,220,90,230],[74,128,128,0],[75,48,48,48],
  [76,240,230,210],[77,200,180,150],[78,64,104,64],
];

export function hexToJefColor(hex) {
  const r = parseInt(hex.slice(1, 3), 16);
  const g = parseInt(hex.slice(3, 5), 16);
  const b = parseInt(hex.slice(5, 7), 16);
  let best = 1, bestD = Infinity;
  for (const [code, pr, pg, pb] of JEF_PALETTE) {
    const d = (r - pr) ** 2 + (g - pg) ** 2 + (b - pb) ** 2;
    if (d < bestD) { bestD = d; best = code; }
  }
  return best;
}

// ─── Brand Palettes ──────────────────────────────────────────────────────────
export const PALETTES = {
  janome: {
    label: 'Janome',
    colors: [
      {n:'Black',h:'#000000',code:'J-01'},{n:'White',h:'#FFFFFF',code:'J-02'},
      {n:'Yellow',h:'#FFFF17',code:'J-03'},{n:'Orange',h:'#FA9F60',code:'J-04'},
      {n:'Olive Green',h:'#5C7649',code:'J-05'},{n:'Bright Green',h:'#40C030',code:'J-06'},
      {n:'Sky Blue',h:'#65C2C8',code:'J-07'},{n:'Purple',h:'#AC80BE',code:'J-08'},
      {n:'Pink',h:'#F5BCCB',code:'J-09'},{n:'Red',h:'#FF0000',code:'J-10'},
      {n:'Brown',h:'#C08000',code:'J-11'},{n:'Blue',h:'#0000F0',code:'J-12'},
      {n:'Gold',h:'#E4C35D',code:'J-13'},{n:'Sienna',h:'#A52A2A',code:'J-14'},
      {n:'Light Purple',h:'#D5B0D4',code:'J-15'},{n:'Light Yellow',h:'#FCF294',code:'J-16'},
      {n:'Light Peach',h:'#F0D0C0',code:'J-17'},{n:'Peach',h:'#FFC000',code:'J-18'},
      {n:'Beige',h:'#C9A480',code:'J-19'},{n:'Wine',h:'#9B3D4B',code:'J-20'},
      {n:'Pale Blue',h:'#A0B8CC',code:'J-21'},{n:'Lime',h:'#7FC21C',code:'J-22'},
      {n:'Lilac',h:'#E5C5CA',code:'J-23'},{n:'Deep Purple',h:'#4D4160',code:'J-24'},
      {n:'Salmon',h:'#EE9294',code:'J-25'},{n:'Rust',h:'#A74F2F',code:'J-26'},
      {n:'Ivory',h:'#FFF9E3',code:'J-27'},{n:'Dark Blue',h:'#004986',code:'J-28'},
      {n:'Mauve',h:'#AC62A6',code:'J-29'},{n:'Sage',h:'#ADB797',code:'J-30'},
      {n:'Steel Blue',h:'#418299',code:'J-31'},{n:'Dark Green',h:'#008040',code:'J-32'},
      {n:'Dark Navy',h:'#0E0864',code:'J-33'},{n:'Teal',h:'#8CC6D3',code:'J-34'},
      {n:'Dark Gold',h:'#E1C484',code:'J-35'},{n:'Deep Rose',h:'#FF7BB2',code:'J-36'},
      {n:'Deep Red',h:'#FF0000',code:'J-37'},{n:'Rust Orange',h:'#D15C00',code:'J-38'},
      {n:'Forest Green',h:'#008000',code:'J-39'},{n:'Chocolate',h:'#71512E',code:'J-40'},
      {n:'Mustard',h:'#F0DC50',code:'J-41'},{n:'Coral',h:'#FF7F50',code:'J-42'},
      {n:'Canary',h:'#FFFF17',code:'J-43'},{n:'Aquamarine',h:'#0080C0',code:'J-44'},
      {n:'Navy',h:'#000080',code:'J-45'},{n:'Violet',h:'#CC00FF',code:'J-46'},
      {n:'Hot Pink',h:'#FF80C8',code:'J-47'},{n:'Green',h:'#008000',code:'J-48'},
      {n:'Tangerine',h:'#FFA541',code:'J-49'},{n:'Maroon',h:'#803030',code:'J-50'},
    ],
  },
  brother: {
    label: 'Brother',
    colors: [
      {n:'Prussian Blue',h:'#1A3768',code:'B-007'},{n:'Blue',h:'#0B55C4',code:'B-405'},
      {n:'Ultramarine',h:'#183EC0',code:'B-420'},{n:'Cornflower Blue',h:'#5584C0',code:'B-070'},
      {n:'Baby Blue',h:'#82AFCD',code:'B-017'},{n:'Aquamarine',h:'#5EA7A8',code:'B-507'},
      {n:'Teal Green',h:'#2D957F',code:'B-534'},{n:'Emerald Green',h:'#20913C',code:'B-208'},
      {n:'Green',h:'#33A500',code:'B-515'},{n:'Lime Green',h:'#8DCA00',code:'B-502'},
      {n:'Olive',h:'#636B2E',code:'B-519'},{n:'Yellow',h:'#FFC800',code:'B-205'},
      {n:'Gold',h:'#D0A500',code:'B-214'},{n:'Orange',h:'#FF7D00',code:'B-209'},
      {n:'Tangerine',h:'#FF5500',code:'B-126'},{n:'Vermilion',h:'#E80000',code:'B-030'},
      {n:'Red',h:'#C71D00',code:'B-206'},{n:'Magenta',h:'#C73778',code:'B-620'},
      {n:'Pink',h:'#FFA0C0',code:'B-223'},{n:'Rose',h:'#FF7090',code:'B-225'},
      {n:'Flesh',h:'#EEB888',code:'B-018'},{n:'Cream',h:'#F5E8C0',code:'B-010'},
      {n:'White',h:'#FFFFFF',code:'B-001'},{n:'Light Gray',h:'#C0C0C0',code:'B-399'},
      {n:'Gray',h:'#808080',code:'B-707'},{n:'Dark Gray',h:'#404040',code:'B-058'},
      {n:'Black',h:'#000000',code:'B-020'},{n:'Chocolate',h:'#5C320A',code:'B-058'},
      {n:'Brown',h:'#834B2A',code:'B-328'},{n:'Tan',h:'#B0885C',code:'B-348'},
      {n:'Purple',h:'#6B2FA0',code:'B-614'},{n:'Lavender',h:'#9878B8',code:'B-607'},
    ],
  },
  isacord: {
    label: 'Isacord',
    colors: [
      {n:'White',h:'#FFFFFF',code:'0010'},{n:'Eggshell',h:'#FFF8E8',code:'0101'},
      {n:'Cream',h:'#FFFDD0',code:'0660'},{n:'Buttercup',h:'#FFE44D',code:'0600'},
      {n:'Canary',h:'#FFEF00',code:'0501'},{n:'Lemon',h:'#FFF44F',code:'0220'},
      {n:'Daffodil',h:'#FFD700',code:'0700'},{n:'Gold',h:'#DAA520',code:'0704'},
      {n:'Old Gold',h:'#CFB53B',code:'0721'},{n:'Honey Gold',h:'#EB9605',code:'0811'},
      {n:'Tangerine',h:'#FF9966',code:'1010'},{n:'Spanish Tile',h:'#CE5B28',code:'1114'},
      {n:'Coral',h:'#FF6F61',code:'1305'},{n:'Salmon',h:'#FA8072',code:'1352'},
      {n:'Shrimp Pink',h:'#FFB3AB',code:'1840'},{n:'Petal Pink',h:'#FADADD',code:'2170'},
      {n:'Carnation',h:'#FFA6C9',code:'2220'},{n:'Hot Pink',h:'#FF69B4',code:'2520'},
      {n:'Magenta',h:'#FF0090',code:'2700'},{n:'Cranberry',h:'#9C0050',code:'2500'},
      {n:'Country Red',h:'#B22222',code:'1902'},{n:'Fire Engine',h:'#CE1126',code:'1800'},
      {n:'Cardinal',h:'#C41E3A',code:'1903'},{n:'Poinsettia',h:'#CC0000',code:'1906'},
      {n:'Bordeaux',h:'#6C2E1F',code:'2115'},{n:'Chocolate',h:'#5C3317',code:'1346'},
      {n:'Cinnamon',h:'#8B4513',code:'1154'},{n:'Penny',h:'#A0522D',code:'1134'},
      {n:'Meringue',h:'#F3E5AB',code:'1060'},{n:'Champagne',h:'#F7E7CE',code:'0870'},
      {n:'Khaki',h:'#C3B091',code:'0651'},{n:'Flax',h:'#EEDC82',code:'0552'},
      {n:'Toffee',h:'#755139',code:'0933'},{n:'Bark',h:'#563C2A',code:'1375'},
      {n:'Mahogany',h:'#420C09',code:'1565'},{n:'Black',h:'#000000',code:'0020'},
      {n:'Charcoal',h:'#36454F',code:'0112'},{n:'Smoke',h:'#738276',code:'0108'},
      {n:'Ash',h:'#B2BEB5',code:'0142'},{n:'Fog',h:'#D2D2CF',code:'0182'},
      {n:'Sterling',h:'#C0C0C0',code:'0150'},{n:'Silver',h:'#D3D3D3',code:'0145'},
      {n:'Light Navy',h:'#4F6D8E',code:'3732'},{n:'Blue Ribbon',h:'#0066CC',code:'3612'},
      {n:'Royal Blue',h:'#002FA7',code:'3544'},{n:'Imperial Blue',h:'#000080',code:'3323'},
      {n:'Navy',h:'#000033',code:'3355'},{n:'Caribbean Blue',h:'#1AC5B0',code:'4620'},
      {n:'Jade',h:'#00A86B',code:'5230'},{n:'Emerald',h:'#046307',code:'5415'},
      {n:'Bright Green',h:'#00CC00',code:'5500'},{n:'Kelly Green',h:'#4CBB17',code:'5510'},
      {n:'Grass Green',h:'#3F7F00',code:'5633'},{n:'Evergreen',h:'#0B4D26',code:'5555'},
      {n:'Forest Green',h:'#014421',code:'5374'},{n:'Olive Drab',h:'#6B8E23',code:'0453'},
      {n:'Sage',h:'#BCB88A',code:'0454'},{n:'Moss',h:'#8A9A5B',code:'5552'},
      {n:'Light Aqua',h:'#93E9BE',code:'5050'},{n:'Lavender',h:'#B57EDC',code:'3045'},
      {n:'Orchid',h:'#DA70D6',code:'2810'},{n:'Violet',h:'#8000FF',code:'3114'},
      {n:'Deep Purple',h:'#36013F',code:'3114'},{n:'Dusty Grape',h:'#715D80',code:'2764'},
      {n:'Plum',h:'#660066',code:'2600'},{n:'Wine',h:'#722F37',code:'2115'},
    ],
  },
};

export const DEFAULT_PALETTE = 'janome';
