/**
 * Design catalog — 50 items across 6 categories.
 * Each entry defines the prompt and recommended settings for generation.
 * The embroidery suffix (including exact colour count) is added automatically.
 *
 * numColors rationale: count black outline + each distinct fill region.
 * The prompt suffix tells Gemini the exact count so KMeans doesn't have to merge.
 *
 * Once generated + saved, items appear in the Library with their
 * stitch preview and download link.
 */

export const CATEGORIES = [
  { id: 'florals',        label: 'Florals',         icon: '🌸' },
  { id: 'birds-insects',  label: 'Birds & Insects',  icon: '🦋' },
  { id: 'animals',        label: 'Animals',          icon: '🦊' },
  { id: 'botanicals',     label: 'Botanicals',       icon: '🍃' },
  { id: 'folk-art',       label: 'Folk Art',         icon: '🎨' },
  { id: 'geometric',      label: 'Geometric',        icon: '✦'  },
];

// Default settings shared by most designs
const D = {
  hoopKey:      '4x4',
  densityMm:    0.4,
  outline:      'running',
  minFeatureMm: 1.5,
};

export const CATALOG = [

  // ─── Florals (10) ────────────────────────────────────────────────────────
  {
    id: 'sunflower',
    name: 'Sunflower',
    category: 'florals',
    description: 'Bold single sunflower with golden petals and dark seed centre',
    prompt: 'a single sunflower with bold golden petals and a dark brown seed centre, green stem and two leaves, centered on white',
    settings: { ...D, numColors: 5 }, // black outline, brown centre, yellow petals, dark green, light green
  },
  {
    id: 'red-rose',
    name: 'Red Rose',
    category: 'florals',
    description: 'Classic red rose with dark green leaves',
    prompt: 'a classic red rose in full bloom with two dark green leaves, centered on white',
    settings: { ...D, numColors: 4 }, // black outline, red petals, dark red shadow, dark green
  },
  {
    id: 'daisy',
    name: 'Daisy',
    category: 'florals',
    description: 'Simple white daisy with yellow centre',
    prompt: 'a single white daisy flower with a bright yellow centre and a short green stem, centered on white',
    settings: { ...D, numColors: 4 }, // black outline, white petals, yellow centre, green stem
  },
  {
    id: 'lavender-sprig',
    name: 'Lavender Sprig',
    category: 'florals',
    description: 'Elegant lavender sprig in purple and grey-green',
    prompt: 'a sprig of lavender with purple flower heads and grey-green stems, botanical illustration style',
    settings: { ...D, numColors: 4 }, // black, purple, light purple, grey-green
  },
  {
    id: 'cherry-blossom',
    name: 'Cherry Blossom Branch',
    category: 'florals',
    description: 'Delicate cherry blossom branch with pink blooms',
    prompt: 'a cherry blossom branch with soft pink flowers and dark brown bark, Japanese botanical style',
    settings: { ...D, numColors: 4 }, // dark brown bark, light pink, mid pink, black outline
  },
  {
    id: 'poppy',
    name: 'Poppy',
    category: 'florals',
    description: 'Vivid red poppy with black centre',
    prompt: 'a single bright red poppy flower with a black centre and green stem, bold and graphic',
    settings: { ...D, numColors: 3 }, // black (outline + centre), red, green
  },
  {
    id: 'tulip',
    name: 'Tulip',
    category: 'florals',
    description: 'Classic tulip in red with green stem',
    prompt: 'a single classic red tulip with two green leaves and a long straight stem, centered',
    settings: { ...D, numColors: 3 }, // black outline, red, green
  },
  {
    id: 'lotus',
    name: 'Lotus Flower',
    category: 'florals',
    description: 'Open lotus in pink and white with yellow stamens',
    prompt: 'an open lotus flower with pink outer petals, white inner petals and yellow stamens, symmetrical, centered on white',
    settings: { ...D, numColors: 4 }, // black, pink, white inner, yellow stamens
  },
  {
    id: 'wildflower-bunch',
    name: 'Wildflower Bunch',
    category: 'florals',
    description: 'Small hand-tied bunch of mixed wildflowers',
    prompt: 'a small hand-tied bunch of mixed wildflowers including daisies, buttercups and cornflowers, tied with a simple ribbon',
    settings: { ...D, numColors: 5, hoopKey: '5x7' }, // black, blue, yellow, white, green
  },
  {
    id: 'peony',
    name: 'Peony',
    category: 'florals',
    description: 'Full-bloom peony in blush pink',
    prompt: 'a full-bloom peony flower in blush pink with layered petals in light and dark pink and dark green leaves',
    settings: { ...D, numColors: 5 }, // black, dark green, light pink, mid pink, dark pink
  },

  // ─── Birds & Insects (10) ─────────────────────────────────────────────────
  {
    id: 'robin',
    name: 'Robin',
    category: 'birds-insects',
    description: 'Cheerful robin redbreast perched on a twig',
    prompt: 'a cheerful robin redbreast with bright orange chest perched on a bare twig, facing right',
    settings: { ...D, numColors: 5 }, // black, orange breast, brown back, cream belly, brown twig
  },
  {
    id: 'monarch-butterfly',
    name: 'Monarch Butterfly',
    category: 'birds-insects',
    description: 'Monarch butterfly with wings open, bold orange and black',
    prompt: 'a monarch butterfly with wings open showing bold orange and black pattern with white dot markings',
    settings: { ...D, numColors: 4 }, // black, orange, white dots, dark body
  },
  {
    id: 'honeybee',
    name: 'Honeybee',
    category: 'birds-insects',
    description: 'Plump honeybee in yellow and black with wings',
    prompt: 'a plump honeybee with yellow and black stripes, translucent wings with dark veins, and fuzzy body, centered',
    settings: { ...D, numColors: 4 }, // black, yellow, amber/brown body, pale wing
  },
  {
    id: 'hummingbird',
    name: 'Hummingbird',
    category: 'birds-insects',
    description: 'Emerald green hummingbird visiting a flower',
    prompt: 'an emerald green hummingbird hovering beside a red tubular flower, wings blurred',
    settings: { ...D, numColors: 4 }, // black, emerald, ruby red, dark green
  },
  {
    id: 'bluebird',
    name: 'Bluebird',
    category: 'birds-insects',
    description: 'Eastern bluebird in bright blue and orange',
    prompt: 'an eastern bluebird perched on a branch, bright blue back and wings, orange breast, white belly, facing left',
    settings: { ...D, numColors: 5 }, // black, bright blue, orange, white belly, brown branch
  },
  {
    id: 'owl',
    name: 'Barn Owl',
    category: 'birds-insects',
    description: 'Wide-eyed barn owl face, white and tawny',
    prompt: 'a barn owl face front-on with wide dark eyes, white heart-shaped face and tawny brown feathers',
    settings: { ...D, numColors: 4 }, // black (eyes+outline), white face, tawny, cream
  },
  {
    id: 'ladybug',
    name: 'Ladybug',
    category: 'birds-insects',
    description: 'Classic red ladybug with black spots',
    prompt: 'a bright red ladybug with black spots viewed from above on a green leaf',
    settings: { ...D, numColors: 3 }, // black (outline+spots), red, green
  },
  {
    id: 'dragonfly',
    name: 'Dragonfly',
    category: 'birds-insects',
    description: 'Iridescent dragonfly with delicate wings',
    prompt: 'a dragonfly with a teal iridescent body and four pale wings with dark veins, viewed from above',
    settings: { ...D, numColors: 4 }, // black, teal, dark teal, pale wing
  },
  {
    id: 'swallow',
    name: 'Swallow in Flight',
    category: 'birds-insects',
    description: 'Barn swallow mid-flight, blue and white',
    prompt: 'a barn swallow in mid-flight with dark navy blue back, rust orange throat, white belly and forked tail, side view',
    settings: { ...D, numColors: 4 }, // dark navy, rust orange, white belly, black
  },
  {
    id: 'bumblebee',
    name: 'Bumblebee on Clover',
    category: 'birds-insects',
    description: 'Round bumblebee on a pink clover flower',
    prompt: 'a round fluffy bumblebee sitting on a pink clover flower with a green stem, bold cartoon style',
    settings: { ...D, numColors: 4 }, // black, yellow, pink flower, green stem
  },

  // ─── Animals (8) ──────────────────────────────────────────────────────────
  {
    id: 'sitting-cat',
    name: 'Sitting Cat',
    category: 'animals',
    description: 'Simple silhouette of a cat sitting upright',
    prompt: 'a simple orange tabby cat sitting upright facing forward, bold outline with dark orange stripes',
    settings: { ...D, numColors: 3 }, // black outline, orange, dark orange stripes
  },
  {
    id: 'fox',
    name: 'Fox Portrait',
    category: 'animals',
    description: 'Alert red fox face looking forward',
    prompt: 'a red fox face portrait looking directly forward with white muzzle and dark nose, bold and graphic',
    settings: { ...D, numColors: 4 }, // black, red-orange, white muzzle, dark brown ear tips
  },
  {
    id: 'hedgehog',
    name: 'Hedgehog',
    category: 'animals',
    description: 'Curled hedgehog with spines and tiny nose',
    prompt: 'a small hedgehog walking with spiny dark brown back, cream belly and tiny black eyes, side view',
    settings: { ...D, numColors: 3 }, // black, dark brown, cream belly
  },
  {
    id: 'rabbit',
    name: 'Sitting Rabbit',
    category: 'animals',
    description: 'White rabbit with long ears sitting upright',
    prompt: 'a white rabbit sitting upright with long ears with pink inner lining and a round fluffy body, front view',
    settings: { ...D, numColors: 4 }, // black outline+eye, white body, pink inner ear, light grey shadow
  },
  {
    id: 'deer',
    name: 'Deer Head',
    category: 'animals',
    description: 'Elegant deer head with antlers, front view',
    prompt: 'an elegant deer head with antlers facing forward, warm brown with a white chin patch, graphic style',
    settings: { ...D, numColors: 4 }, // black, warm brown, dark brown antlers, white chin
  },
  {
    id: 'bear-cub',
    name: 'Bear Cub',
    category: 'animals',
    description: 'Round-faced brown bear cub sitting',
    prompt: 'a round-faced brown bear cub sitting with small ears and a simple smiling expression',
    settings: { ...D, numColors: 3 }, // black, dark brown, medium brown muzzle
  },
  {
    id: 'squirrel',
    name: 'Squirrel with Acorn',
    category: 'animals',
    description: 'Russet squirrel holding an acorn',
    prompt: 'a russet squirrel sitting upright holding an acorn with a large bushy tail curled over its back',
    settings: { ...D, numColors: 4 }, // black, russet, pale belly, brown acorn
  },
  {
    id: 'frog',
    name: 'Frog on Lily Pad',
    category: 'animals',
    description: 'Green frog perched on a lily pad',
    prompt: 'a bright green frog sitting on a dark green round lily pad with a small white water lily flower beside it',
    settings: { ...D, numColors: 4 }, // black, bright green, dark green, white flower
  },

  // ─── Botanicals (8) ───────────────────────────────────────────────────────
  {
    id: 'autumn-leaf',
    name: 'Autumn Maple Leaf',
    category: 'botanicals',
    description: 'Maple leaf in autumn reds and oranges',
    prompt: 'a single maple leaf in autumn colours of deep red, orange and gold with visible dark veins',
    settings: { ...D, numColors: 4 }, // dark red, orange, gold, dark vein/outline
  },
  {
    id: 'mushroom',
    name: 'Toadstool',
    category: 'botanicals',
    description: 'Classic red toadstool with white spots',
    prompt: 'a classic red toadstool mushroom with white spots, a pale cream underside and a brown stem on green grass',
    settings: { ...D, numColors: 5 }, // black, red cap, white spots, cream gills, brown stem, green
  },
  {
    id: 'fern-frond',
    name: 'Fern Frond',
    category: 'botanicals',
    description: 'Single unfurling fern frond in deep green',
    prompt: 'a single fern frond with symmetric leaflets on a curved stem, deep forest green, botanical print style',
    settings: { ...D, numColors: 3, outline: 'running' }, // black, dark green, medium green
  },
  {
    id: 'acorn',
    name: 'Acorn',
    category: 'botanicals',
    description: 'Acorn with oak leaf, autumn browns',
    prompt: 'an acorn with its textured cap next to a lobed oak leaf, warm brown and tan tones, botanical style',
    settings: { ...D, numColors: 4 }, // black, dark brown cap, tan body, green oak leaf
  },
  {
    id: 'strawberry',
    name: 'Strawberry',
    category: 'botanicals',
    description: 'Plump red strawberry with green leaves',
    prompt: 'a plump bright red strawberry with small yellow seeds and a green leafy crown, centered',
    settings: { ...D, numColors: 4 }, // black, red, yellow seeds, green crown
  },
  {
    id: 'pinecone',
    name: 'Pinecone',
    category: 'botanicals',
    description: 'Detailed pinecone with overlapping scales',
    prompt: 'a brown pinecone with clearly defined overlapping scales in dark and medium brown and a short stem, botanical illustration',
    settings: { ...D, numColors: 3 }, // black, dark brown, medium brown
  },
  {
    id: 'berries-branch',
    name: 'Berry Branch',
    category: 'botanicals',
    description: 'Branch with clusters of deep red berries and leaves',
    prompt: 'a branch with clusters of small dark red berries and glossy green leaves, winter botanical',
    settings: { ...D, numColors: 4 }, // black, dark red berries, green leaves, brown branch
  },
  {
    id: 'succulent',
    name: 'Succulent Rosette',
    category: 'botanicals',
    description: 'Top-down view of a rosette succulent',
    prompt: 'a succulent plant viewed from directly above showing a perfect rosette of thick leaves in grey-green and blue-green',
    settings: { ...D, numColors: 4 }, // black, grey-green outer, blue-green inner, pale centre
  },

  // ─── Folk Art (7) ─────────────────────────────────────────────────────────
  {
    id: 'scandinavian-flower',
    name: 'Scandinavian Rosette',
    category: 'folk-art',
    description: 'Classic Scandinavian folk art flower in red and blue',
    prompt: 'a classic Scandinavian folk art rosette flower in red, blue and white with decorative green leaves, Dala style',
    settings: { ...D, numColors: 5 }, // black, red, blue, white, green
  },
  {
    id: 'folk-bird',
    name: 'Folk Art Bird',
    category: 'folk-art',
    description: 'Stylised folk art bird with decorative tail feathers',
    prompt: 'a stylised folk art bird with decorative curved tail feathers and floral details, Eastern European style in red, gold and blue',
    settings: { ...D, numColors: 5 }, // black, red, gold, blue, green accent
  },
  {
    id: 'hex-sign',
    name: 'Pennsylvania Hex',
    category: 'folk-art',
    description: 'Pennsylvania Dutch hex sign with tulips and stars',
    prompt: 'a Pennsylvania Dutch hex sign with tulips, a six-pointed star and decorative border, circular, bold primary colours red blue yellow green',
    settings: { ...D, numColors: 6 }, // black, red, blue, yellow, green, white
  },
  {
    id: 'mexican-marigold',
    name: 'Día de Muertos Marigold',
    category: 'folk-art',
    description: 'Vibrant orange marigold in Mexican folk style',
    prompt: 'a vibrant orange and yellow marigold flower in Mexican Día de los Muertos folk art style with decorative green leaves and red accents',
    settings: { ...D, numColors: 5 }, // black, orange, yellow, green, red accent
  },
  {
    id: 'matryoshka',
    name: 'Matryoshka Doll',
    category: 'folk-art',
    description: 'Classic Russian nesting doll in red and gold',
    prompt: 'a classic Russian matryoshka nesting doll in red with gold decoration, pink face and colourful floral folk art patterns on a white background',
    settings: { ...D, numColors: 6 }, // black, red, gold, pink face, blue flowers, green leaves
  },
  {
    id: 'folk-horse',
    name: 'Dala Horse',
    category: 'folk-art',
    description: 'Swedish Dala horse in traditional red with floral decoration',
    prompt: 'a Swedish Dala horse in traditional bright red with blue, yellow and green flower and saddle decoration, simple bold outline',
    settings: { ...D, numColors: 5 }, // black, red, blue, yellow, green
  },
  {
    id: 'otomi-deer',
    name: 'Otomí Deer',
    category: 'folk-art',
    description: 'Mexican Otomí embroidery style deer with flowers',
    prompt: 'a deer in Mexican Otomí embroidery style surrounded by stylised flowers and birds in red, pink, blue and green, bold outline',
    settings: { ...D, numColors: 6 }, // black, deer colour, red, pink, blue, green
  },

  // ─── Geometric (7) ────────────────────────────────────────────────────────
  {
    id: 'mandala',
    name: 'Mandala',
    category: 'geometric',
    description: 'Eight-fold mandala in indigo and gold',
    prompt: 'a symmetrical eight-fold mandala with geometric petal shapes, in deep indigo, medium indigo and gold on white, bold clean lines',
    settings: { ...D, numColors: 4 }, // black, deep indigo, medium indigo, gold
  },
  {
    id: 'hex-grid',
    name: 'Honeycomb',
    category: 'geometric',
    description: 'Interlocking hexagons in amber and honey tones',
    prompt: 'a honeycomb pattern of interlocking hexagons in amber, gold and honey tones, simple and bold',
    settings: { ...D, numColors: 3 }, // black outline, amber, gold
  },
  {
    id: 'star-burst',
    name: 'Eight-Pointed Star',
    category: 'geometric',
    description: 'Classic eight-pointed star with radiating points',
    prompt: 'a bold eight-pointed star with alternating long and short points in deep teal and cream, geometric quilt pattern',
    settings: { ...D, numColors: 3 }, // black, deep teal, cream
  },
  {
    id: 'celtic-knot',
    name: 'Celtic Knot',
    category: 'geometric',
    description: 'Interlaced Celtic trinity knot in forest green',
    prompt: 'a Celtic trinity knot with clean interlaced bands in forest green with a thin gold outline, circular composition',
    settings: { ...D, numColors: 3 }, // black, forest green, gold outline
  },
  {
    id: 'diamond-grid',
    name: 'Diamond Lattice',
    category: 'geometric',
    description: 'Repeating diamond lattice in navy and white',
    prompt: 'a repeating diamond lattice pattern in navy blue and white with small gold dot accents at intersections',
    settings: { ...D, numColors: 3 }, // navy, white, gold dots
  },
  {
    id: 'pinwheel',
    name: 'Pinwheel',
    category: 'geometric',
    description: 'Four-blade pinwheel in bright primary colours',
    prompt: 'a four-blade pinwheel with alternating red and blue blades and a yellow centre, simple bold shapes',
    settings: { ...D, numColors: 3 }, // black, red, blue, yellow — 4 really
  },
  {
    id: 'compass-rose',
    name: 'Compass Rose',
    category: 'geometric',
    description: 'Nautical compass rose in navy and gold',
    prompt: 'a nautical compass rose with sixteen points in navy blue and gold, clean sharp lines on white',
    settings: { ...D, numColors: 3 }, // black, navy, gold
  },
];

/** Look up catalog entry by id */
export function getCatalogEntry(id) {
  return CATALOG.find(e => e.id === id) ?? null;
}
