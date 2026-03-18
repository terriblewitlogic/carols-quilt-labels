// ─── Structured field definitions ────────────────────────────────────────────
export const ESSENTIAL_FIELDS = [
  { key: 'quilterName', label: 'Quilter Name', placeholder: 'Jane Smith', icon: '✂' },
  { key: 'dateCompleted', label: 'Date Completed', placeholder: 'March 2026', icon: '📅' },
  { key: 'location', label: 'City, State/Country', placeholder: 'Portland, OR', icon: '📍' },
];

export const STANDARD_FIELDS = [
  { key: 'quiltName', label: 'Quilt Name', placeholder: 'Starry Night', icon: '🏷' },
  { key: 'patternDesigner', label: 'Pattern Designer', placeholder: 'Original design', icon: '📐' },
  { key: 'recipient', label: 'For / Recipient', placeholder: 'For Sarah', icon: '🎁' },
  { key: 'occasion', label: 'Occasion', placeholder: 'Birthday', icon: '🎉' },
  { key: 'quiltedBy', label: 'Quilted By', placeholder: 'Quilted by...', icon: '🧵' },
];

export const OPTIONAL_FIELDS = [
  { key: 'message', label: 'Personal Message', placeholder: 'Made with love...', icon: '💌', multiline: true },
  { key: 'careInstructions', label: 'Care Instructions', placeholder: 'Machine wash cold, tumble dry low', icon: '🧼' },
  { key: 'fabricCollection', label: 'Fabric Collection', placeholder: 'Kona Cotton', icon: '🎨' },
  { key: 'guildName', label: 'Guild / Group', placeholder: 'Portland Modern Quilt Guild', icon: '👥' },
  { key: 'copyright', label: 'Copyright', placeholder: '© 2026', icon: '©' },
  { key: 'quiltNumber', label: 'Quilt Number', placeholder: '#42', icon: '#' },
];

// ─── Occasion templates ──────────────────────────────────────────────────────
export const TEMPLATES = [
  {
    id: 'general',
    label: 'General Label',
    description: 'Standard quilt label with name, date, and location',
    icon: '🏷',
    activeFields: ['quilterName', 'dateCompleted', 'location', 'quiltName'],
    defaults: { quilterName: 'Jane Smith', quiltName: 'Starry Night', dateCompleted: new Date().getFullYear().toString(), location: 'Portland, OR' },
    suggestedElements: ['heart-simple', 'vine-trail'],
    layout: [
      { field: 'quiltName', fontScale: 1.2, font: 'serif' },
      { field: 'quilterName', fontScale: 1.0, font: 'times' },
      { field: 'dateCompleted', fontScale: 0.75, font: 'sans' },
      { field: 'location', fontScale: 0.7, font: 'sans' },
    ],
  },
  {
    id: 'baby',
    label: 'Baby Quilt',
    description: 'Welcome a new little one with name, birth date, and details',
    icon: '👶',
    activeFields: ['quilterName', 'dateCompleted', 'recipient', 'occasion', 'message'],
    defaults: { childName: 'Baby Emma', birthDate: 'March 15, 2026', birthWeight: '7 lbs 4 oz', parents: 'Sarah & James', quilterName: 'Grandma Sue', message: 'Made with Love', occasion: 'Welcome Baby' },
    extraFields: [
      { key: 'childName', label: 'Baby Name', placeholder: 'Baby Emma' },
      { key: 'birthDate', label: 'Birth Date', placeholder: 'March 15, 2026' },
      { key: 'birthWeight', label: 'Weight', placeholder: '7 lbs 4 oz' },
      { key: 'parents', label: 'Parents', placeholder: 'Sarah & James' },
    ],
    suggestedElements: ['star-simple', 'heart-simple'],
    layout: [
      { field: 'childName', fontScale: 1.3, font: 'serif' },
      { field: 'birthDate', fontScale: 0.85, font: 'times' },
      { field: 'birthWeight', fontScale: 0.7, font: 'sans' },
      { field: 'parents', fontScale: 0.8, font: 'times' },
      { field: 'quilterName', fontScale: 0.7, font: 'sans' },
      { field: 'message', fontScale: 0.65, font: 'serif' },
    ],
  },
  {
    id: 'wedding',
    label: 'Wedding Quilt',
    description: 'Celebrate the happy couple',
    icon: '💒',
    activeFields: ['quilterName', 'dateCompleted', 'recipient', 'occasion', 'message'],
    defaults: { coupleName: 'Sarah & James', weddingDate: 'June 15, 2026', quilterName: 'Your Name', message: 'Wishing you joy', occasion: 'Wedding' },
    extraFields: [
      { key: 'coupleName', label: 'Couple Names', placeholder: 'Sarah & James' },
      { key: 'weddingDate', label: 'Wedding Date', placeholder: 'June 15, 2026' },
    ],
    suggestedElements: ['heart-double', 'vine-trail'],
    layout: [
      { field: 'coupleName', fontScale: 1.2, font: 'serif' },
      { field: 'weddingDate', fontScale: 0.9, font: 'times' },
      { field: 'quilterName', fontScale: 0.7, font: 'sans' },
      { field: 'message', fontScale: 0.65, font: 'serif' },
    ],
  },
  {
    id: 'memorial',
    label: 'Memorial Quilt',
    description: 'In loving memory',
    icon: '🕊',
    activeFields: ['quilterName', 'dateCompleted', 'recipient', 'message'],
    defaults: { message: 'In Loving Memory', honoree: 'Grandma Rose', years: '1935 – 2025', quilterName: 'Your Name' },
    extraFields: [
      { key: 'honoree', label: 'In Memory Of', placeholder: 'Grandma Rose' },
      { key: 'years', label: 'Years', placeholder: '1935 – 2025' },
    ],
    suggestedElements: ['dove', 'flower-rose'],
    layout: [
      { field: 'message', fontScale: 1.0, font: 'serif' },
      { field: 'honoree', fontScale: 1.2, font: 'times' },
      { field: 'years', fontScale: 0.85, font: 'sans' },
      { field: 'quilterName', fontScale: 0.7, font: 'sans' },
    ],
  },
  {
    id: 'holiday',
    label: 'Holiday Quilt',
    description: 'Seasonal and holiday quilts',
    icon: '🎄',
    activeFields: ['quilterName', 'dateCompleted', 'recipient', 'occasion', 'message'],
    defaults: { occasion: 'Christmas 2026', recipient: 'The Smith Family', message: 'Warmth & Joy', quilterName: 'Your Name', dateCompleted: new Date().getFullYear().toString() },
    suggestedElements: ['star-simple', 'snowflake'],
    layout: [
      { field: 'occasion', fontScale: 1.1, font: 'serif' },
      { field: 'recipient', fontScale: 0.9, font: 'times' },
      { field: 'message', fontScale: 0.8, font: 'serif' },
      { field: 'quilterName', fontScale: 0.7, font: 'sans' },
      { field: 'dateCompleted', fontScale: 0.65, font: 'sans' },
    ],
  },
  {
    id: 'quilts-of-valor',
    label: 'Quilts of Valor',
    description: 'Honoring service members (QOVF compliant)',
    icon: '🇺🇸',
    activeFields: ['quilterName', 'dateCompleted', 'recipient', 'quiltedBy'],
    defaults: { occasion: 'Quilt of Valor', awardedTo: 'SGT John Smith', awardDate: 'November 11, 2026', quilterName: 'Your Name', quiltedBy: 'Local QOV Group' },
    extraFields: [
      { key: 'awardedTo', label: 'Awarded To', placeholder: 'SGT John Smith' },
      { key: 'awardedBy', label: 'Awarded By', placeholder: 'Local QOV Group' },
      { key: 'awardDate', label: 'Award Date', placeholder: 'November 11, 2026' },
    ],
    suggestedElements: ['star-simple'],
    layout: [
      { field: 'title', fontScale: 1.1, font: 'sans', fixedText: 'Quilt of Valor' },
      { field: 'awardedTo', fontScale: 1.0, font: 'serif' },
      { field: 'awardDate', fontScale: 0.8, font: 'sans' },
      { field: 'quilterName', fontScale: 0.7, font: 'sans' },
      { field: 'quiltedBy', fontScale: 0.7, font: 'sans' },
    ],
  },
];
