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
    prompt: 'a single sunflower with bold golden-yellow petals arranged in a perfect radial ring, a flat warm amber-brown circular seed centre, a straight green stem with two identical matching leaves on either side, bold black outlines only, centered on white',
    settings: { ...D, numColors: 5 }, // black outline, amber-brown centre, golden-yellow petals, green leaves/stem
  },
  {
    id: 'red-rose',
    name: 'Red Rose',
    category: 'florals',
    description: 'Classic red rose with dark green leaves',
    prompt: 'a classic red rose in full bloom viewed from the front, perfectly centered with uniform overlapping petals in bright red and deep red, two identical dark green leaves one on each side of the stem, centered on white',
    settings: { ...D, numColors: 4 }, // black outline, red petals, dark red shadow, dark green
  },
  {
    id: 'daisy',
    name: 'Daisy',
    category: 'florals',
    description: 'Simple white daisy with yellow centre',
    prompt: 'a single white daisy flower viewed from the front with uniform white petals arranged in a perfect radial ring around a bright yellow circular centre, a short straight green stem, centered on white',
    settings: { ...D, numColors: 4 }, // black outline, white petals, yellow centre, green stem
  },
  {
    id: 'lavender-sprig',
    name: 'Lavender Sprig',
    category: 'florals',
    description: 'Elegant lavender sprig in purple and grey-green',
    prompt: 'a single lavender sprig with a straight grey-green stem, identical paired purple flower buds spaced evenly along both sides of the stem, perfectly upright and centered on white',
    settings: { ...D, numColors: 4 }, // black, purple, light purple, grey-green
  },
  {
    id: 'cherry-blossom',
    name: 'Cherry Blossom Branch',
    category: 'florals',
    description: 'Delicate cherry blossom branch with pink blooms',
    prompt: 'a cherry blossom branch extending symmetrically left and right with matching clusters of soft pink five-petal flowers and dark brown bark, centered on white',
    settings: { ...D, numColors: 4 }, // dark brown bark, light pink, mid pink, black outline
  },
  {
    id: 'poppy',
    name: 'Poppy',
    category: 'florals',
    description: 'Vivid red poppy with black centre',
    prompt: 'a single bright red poppy flower viewed from the front with four uniform rounded petals arranged radially around a flat black circular centre, a straight green stem, centered on white',
    settings: { ...D, numColors: 3 }, // black (outline + centre), red, green
  },
  {
    id: 'tulip',
    name: 'Tulip',
    category: 'florals',
    description: 'Classic tulip in red with green stem',
    prompt: 'a single classic red tulip viewed from the front with a perfectly upright bloom, a long straight green stem and two identical matching green leaves one on each side, centered on white',
    settings: { ...D, numColors: 3 }, // black outline, red, green
  },
  {
    id: 'lotus',
    name: 'Lotus Flower',
    category: 'florals',
    description: 'Open lotus in pink and white with yellow stamens',
    prompt: 'an open lotus flower viewed from the front with perfectly bilateral symmetric pink outer petals, white inner petals and a yellow stamen centre, centered on white',
    settings: { ...D, numColors: 4 }, // black, pink, white inner, yellow stamens
  },
  {
    id: 'wildflower-bunch',
    name: 'Wildflower Bunch',
    category: 'florals',
    description: 'Small hand-tied bunch of mixed wildflowers',
    prompt: 'a small neat hand-tied bunch of mixed wildflowers including daisies, buttercups and cornflowers, stems tied together with a simple ribbon bow, arranged in a balanced fan shape centered on white',
    settings: { ...D, numColors: 5, hoopKey: '5x7' }, // black, blue, yellow, white, green
  },
  {
    id: 'peony',
    name: 'Peony',
    category: 'florals',
    description: 'Full-bloom peony in blush pink',
    prompt: 'a full-bloom peony flower viewed from the front, perfectly centered with uniform layered petals in light pink and dark pink, two identical dark green leaves one on each side of the stem, centered on white',
    settings: { ...D, numColors: 5 }, // black, dark green, light pink, mid pink, dark pink
  },

  // ─── Birds & Insects (10) ─────────────────────────────────────────────────
  {
    id: 'robin',
    name: 'Robin',
    category: 'birds-insects',
    description: 'Cheerful robin redbreast perched on a twig',
    prompt: 'a cheerful robin redbreast perched on a short horizontal twig, clean balanced side profile facing right, bright orange breast, brown back and wings, cream belly, centered on white',
    settings: { ...D, numColors: 5 }, // black, orange breast, brown back, cream belly, brown twig
  },
  {
    id: 'monarch-butterfly',
    name: 'Monarch Butterfly',
    category: 'birds-insects',
    description: 'Monarch butterfly with wings open, bold orange and black',
    prompt: 'a monarch butterfly viewed from directly above with wings fully open, perfectly bilateral symmetric left and right wings showing identical bold orange panels with black veins and matching white dot markings along the edges, centered on white',
    settings: { ...D, numColors: 4 }, // black, orange, white dots, dark body
  },
  {
    id: 'honeybee',
    name: 'Honeybee',
    category: 'birds-insects',
    description: 'Plump honeybee in yellow and black with wings',
    prompt: 'a plump honeybee viewed from directly above, perfectly bilateral symmetric with matching yellow and black striped body, two identical pale wings on each side, centered on white',
    settings: { ...D, numColors: 4 }, // black, yellow, amber/brown body, pale wing
  },
  {
    id: 'hummingbird',
    name: 'Hummingbird',
    category: 'birds-insects',
    description: 'Emerald green hummingbird visiting a flower',
    prompt: 'an emerald green hummingbird in a clean balanced side profile hovering beside a simple red tubular flower, wings spread symmetrically, centered on white',
    settings: { ...D, numColors: 4 }, // black, emerald, ruby red, dark green
  },
  {
    id: 'bluebird',
    name: 'Bluebird',
    category: 'birds-insects',
    description: 'Eastern bluebird in bright blue and orange',
    prompt: 'an eastern bluebird in a clean balanced side profile perched on a short horizontal branch facing left, bright blue back and wings, orange breast, white belly, centered on white',
    settings: { ...D, numColors: 5 }, // black, bright blue, orange, white belly, brown branch
  },
  {
    id: 'owl',
    name: 'Barn Owl',
    category: 'birds-insects',
    description: 'Wide-eyed barn owl face, white and tawny',
    prompt: 'a barn owl face viewed perfectly front-on, bilateral symmetric with matching tawny brown wings on either side, a white heart-shaped face centred on the front, two identical wide dark eyes, centered on white',
    settings: { ...D, numColors: 4 }, // black (eyes+outline), white face, tawny, cream
  },
  {
    id: 'ladybug',
    name: 'Ladybug',
    category: 'birds-insects',
    description: 'Classic red ladybug with black spots',
    prompt: 'a bright red ladybug viewed from directly above, perfectly bilateral symmetric with matching black spots arranged identically on each wing, a central dividing line, centered on white',
    settings: { ...D, numColors: 3 }, // black (outline+spots), red, green
  },
  {
    id: 'dragonfly',
    name: 'Dragonfly',
    category: 'birds-insects',
    description: 'Iridescent dragonfly with delicate wings',
    prompt: 'a dragonfly viewed from directly above, perfectly bilateral symmetric with four pale wings arranged in two identical matching pairs on each side of a teal iridescent body, centered on white',
    settings: { ...D, numColors: 4 }, // black, teal, dark teal, pale wing
  },
  {
    id: 'swallow',
    name: 'Swallow in Flight',
    category: 'birds-insects',
    description: 'Barn swallow mid-flight, blue and white',
    prompt: 'a barn swallow in mid-flight viewed from the front, perfectly bilateral symmetric with matching dark navy blue wings spread evenly on both sides, rust orange throat patch, white belly, forked tail centered below, centered on white',
    settings: { ...D, numColors: 4 }, // dark navy, rust orange, white belly, black
  },
  {
    id: 'bumblebee',
    name: 'Bumblebee on Clover',
    category: 'birds-insects',
    description: 'Round bumblebee on a pink clover flower',
    prompt: 'a round fluffy bumblebee viewed from directly above sitting on a pink clover flower, perfectly bilateral symmetric bee with matching yellow and black stripes and identical wings on each side, straight green stem below, centered on white',
    settings: { ...D, numColors: 4 }, // black, yellow, pink flower, green stem
  },

  // ─── Animals (8) ──────────────────────────────────────────────────────────
  {
    id: 'sitting-cat',
    name: 'Sitting Cat',
    category: 'animals',
    description: 'Simple silhouette of a cat sitting upright',
    prompt: 'an orange tabby cat sitting perfectly upright facing forward, bilateral symmetric with matching dark orange stripes on each side, two identical ears, a centered face with matching eyes, centered on white',
    settings: { ...D, numColors: 3 }, // black outline, orange, dark orange stripes
  },
  {
    id: 'fox',
    name: 'Fox Portrait',
    category: 'animals',
    description: 'Alert red fox face looking forward',
    prompt: 'a red fox face portrait perfectly front-facing and bilateral symmetric, matching red-orange cheeks and ears on each side, a white muzzle centered below, a dark nose, centered on white',
    settings: { ...D, numColors: 4 }, // black, red-orange, white muzzle, dark brown ear tips
  },
  {
    id: 'hedgehog',
    name: 'Hedgehog',
    category: 'animals',
    description: 'Curled hedgehog with spines and tiny nose',
    prompt: 'a small hedgehog in a clean balanced side profile facing right, spiny dark brown back with uniform evenly-spaced spines, cream belly, tiny black dot eye, centered on white',
    settings: { ...D, numColors: 3 }, // black, dark brown, cream belly
  },
  {
    id: 'rabbit',
    name: 'Sitting Rabbit',
    category: 'animals',
    description: 'White rabbit with long ears sitting upright',
    prompt: 'a white rabbit sitting perfectly upright facing forward, bilateral symmetric with two identical long ears with pink inner lining on each side, a round white body, matching front paws, centered on white',
    settings: { ...D, numColors: 4 }, // black outline+eye, white body, pink inner ear, light grey shadow
  },
  {
    id: 'deer',
    name: 'Deer Head',
    category: 'animals',
    description: 'Elegant deer head with antlers, front view',
    prompt: 'an elegant deer head facing perfectly forward, bilateral symmetric with two identical matching antlers branching evenly on each side, warm brown face, white chin patch centered below, centered on white',
    settings: { ...D, numColors: 4 }, // black, warm brown, dark brown antlers, white chin
  },
  {
    id: 'bear-cub',
    name: 'Bear Cub',
    category: 'animals',
    description: 'Round-faced brown bear cub sitting',
    prompt: 'a round-faced brown bear cub sitting perfectly upright facing forward, bilateral symmetric with two identical round ears, matching dark eyes, a centered lighter muzzle, centered on white',
    settings: { ...D, numColors: 3 }, // black, dark brown, medium brown muzzle
  },
  {
    id: 'squirrel',
    name: 'Squirrel with Acorn',
    category: 'animals',
    description: 'Russet squirrel holding an acorn',
    prompt: 'a russet squirrel sitting perfectly upright facing forward, bilateral symmetric, holding an acorn centered in front with both matching paws, a large bushy tail curving symmetrically behind, pale belly centered, centered on white',
    settings: { ...D, numColors: 4 }, // black, russet, pale belly, brown acorn
  },
  {
    id: 'frog',
    name: 'Frog on Lily Pad',
    category: 'animals',
    description: 'Green frog perched on a lily pad',
    prompt: 'a bright green frog sitting perfectly upright on a round dark green lily pad, bilateral symmetric frog facing forward with matching front legs spread evenly on each side, a simple white water lily centered beside it, centered on white',
    settings: { ...D, numColors: 4 }, // black, bright green, dark green, white flower
  },

  // ─── Botanicals (8) ───────────────────────────────────────────────────────
  {
    id: 'autumn-leaf',
    name: 'Autumn Maple Leaf',
    category: 'botanicals',
    description: 'Maple leaf in autumn reds and oranges',
    prompt: 'a single maple leaf perfectly bilateral symmetric about a central vertical vein, matching lobes on each side in deep red and orange with gold tips, dark veins, stem centered below, centered on white',
    settings: { ...D, numColors: 4 }, // dark red, orange, gold, dark vein/outline
  },
  {
    id: 'mushroom',
    name: 'Toadstool',
    category: 'botanicals',
    description: 'Classic red toadstool with white spots',
    prompt: 'a classic red toadstool mushroom viewed front-on, bilateral symmetric with a perfectly domed red cap, evenly distributed white spots on each side, a pale cream underside, a straight brown stem centered below, centered on white',
    settings: { ...D, numColors: 5 }, // black, red cap, white spots, cream gills, brown stem, green
  },
  {
    id: 'fern-frond',
    name: 'Fern Frond',
    category: 'botanicals',
    description: 'Single unfurling fern frond in deep green',
    prompt: 'a single fern frond with a curved central stem and perfectly bilateral symmetric paired leaflets of identical size and shape on each side, deep forest green, centered on white',
    settings: { ...D, numColors: 3, outline: 'running' }, // black, dark green, medium green
  },
  {
    id: 'acorn',
    name: 'Acorn',
    category: 'botanicals',
    description: 'Acorn with oak leaf, autumn browns',
    prompt: 'a single acorn with a textured cap, bilateral symmetric about a central axis with a short centered stem at top, warm dark brown cap and tan body, a symmetrical lobed oak leaf behind it in green, centered on white',
    settings: { ...D, numColors: 4 }, // black, dark brown cap, tan body, green oak leaf
  },
  {
    id: 'strawberry',
    name: 'Strawberry',
    category: 'botanicals',
    description: 'Plump red strawberry with green leaves',
    prompt: 'a plump bright red strawberry perfectly bilateral symmetric, small evenly distributed yellow seeds on each side, a symmetric green leafy crown centered on top, centered on white',
    settings: { ...D, numColors: 4 }, // black, red, yellow seeds, green crown
  },
  {
    id: 'pinecone',
    name: 'Pinecone',
    category: 'botanicals',
    description: 'Detailed pinecone with overlapping scales',
    prompt: 'a brown pinecone perfectly bilateral symmetric about a central vertical axis, identical overlapping scales in dark and medium brown arranged in matching rows on each side, a short centered stem at top, centered on white',
    settings: { ...D, numColors: 3 }, // black, dark brown, medium brown
  },
  {
    id: 'berries-branch',
    name: 'Berry Branch',
    category: 'botanicals',
    description: 'Branch with clusters of deep red berries and leaves',
    prompt: 'a short branch extending symmetrically left and right with matching clusters of small dark red berries and identical green leaves on each side, a short centered stem, centered on white',
    settings: { ...D, numColors: 4 }, // black, dark red berries, green leaves, brown branch
  },
  {
    id: 'succulent',
    name: 'Succulent Rosette',
    category: 'botanicals',
    description: 'Top-down view of a rosette succulent',
    prompt: 'a succulent plant viewed from directly above showing a perfect radially symmetric rosette of thick pointed leaves in grey-green and blue-green radiating evenly from a pale centre, centered on white',
    settings: { ...D, numColors: 4 }, // black, grey-green outer, blue-green inner, pale centre
  },

  // ─── Folk Art (7) ─────────────────────────────────────────────────────────
  {
    id: 'scandinavian-flower',
    name: 'Scandinavian Rosette',
    category: 'folk-art',
    description: 'Classic Scandinavian folk art flower in red and blue',
    prompt: 'a classic Scandinavian folk art rosette flower with perfectly radially symmetric uniform petals alternating red and blue, white detail accents, identical paired green leaves on each side of the stem, Dala style, centered on white',
    settings: { ...D, numColors: 5 }, // black, red, blue, white, green
  },
  {
    id: 'folk-bird',
    name: 'Folk Art Bird',
    category: 'folk-art',
    description: 'Stylised folk art bird with decorative tail feathers',
    prompt: 'a stylised folk art bird facing right in a clean balanced side profile, bold curved tail feathers fanning out symmetrically, matching floral decorations on the body in red, gold and blue, Eastern European style, centered on white',
    settings: { ...D, numColors: 5 }, // black, red, gold, blue, green accent
  },
  {
    id: 'hex-sign',
    name: 'Pennsylvania Hex',
    category: 'folk-art',
    description: 'Pennsylvania Dutch hex sign with tulips and stars',
    prompt: 'a Pennsylvania Dutch hex sign in a perfect circle, six-fold radially symmetric with six identical tulips and a central six-pointed star, bold primary colours red blue yellow green, a circular decorative border, centered on white',
    settings: { ...D, numColors: 6 }, // black, red, blue, yellow, green, white
  },
  {
    id: 'mexican-marigold',
    name: 'Día de Muertos Marigold',
    category: 'folk-art',
    description: 'Vibrant orange marigold in Mexican folk style',
    prompt: 'a vibrant marigold flower in Mexican Día de los Muertos folk art style, perfectly radially symmetric with uniform orange petals and yellow centre, two identical matching green leaves on each side of the stem, red accent dots evenly placed, centered on white',
    settings: { ...D, numColors: 5 }, // black, orange, yellow, green, red accent
  },
  {
    id: 'matryoshka',
    name: 'Matryoshka Doll',
    category: 'folk-art',
    description: 'Classic Russian nesting doll in red and gold',
    prompt: 'a classic Russian matryoshka nesting doll perfectly bilateral symmetric, red body with identical gold decorations on each side, a centered pink oval face at the top, matching blue floral folk art patterns symmetrically placed on each side, centered on white',
    settings: { ...D, numColors: 6 }, // black, red, gold, pink face, blue flowers, green leaves
  },
  {
    id: 'folk-horse',
    name: 'Dala Horse',
    category: 'folk-art',
    description: 'Swedish Dala horse in traditional red with floral decoration',
    prompt: 'a Swedish Dala horse in traditional bright red in a clean balanced side profile facing right, identical matching blue yellow and green floral saddle decorations placed symmetrically on the body, simple bold outline, centered on white',
    settings: { ...D, numColors: 5 }, // black, red, blue, yellow, green
  },
  {
    id: 'otomi-deer',
    name: 'Otomí Deer',
    category: 'folk-art',
    description: 'Mexican Otomí embroidery style deer with flowers',
    prompt: 'a deer in Mexican Otomí embroidery style facing forward, bilateral symmetric with identical stylised flowers on each side in red and pink, matching blue and green leaf motifs arranged symmetrically, bold outline, centered on white',
    settings: { ...D, numColors: 6 }, // black, deer colour, red, pink, blue, green
  },

  // ─── Geometric (7) ────────────────────────────────────────────────────────
  {
    id: 'mandala',
    name: 'Mandala',
    category: 'geometric',
    description: 'Eight-fold mandala in indigo and gold',
    prompt: 'a perfectly eight-fold radially symmetric mandala with identical geometric petal shapes repeating eight times, deep indigo and medium indigo with gold accents, bold clean lines, centered on white',
    settings: { ...D, numColors: 4 }, // black, deep indigo, medium indigo, gold
  },
  {
    id: 'hex-grid',
    name: 'Honeycomb',
    category: 'geometric',
    description: 'Interlocking hexagons in amber and honey tones',
    prompt: 'a honeycomb pattern of perfectly uniform interlocking regular hexagons arranged in a tight symmetric grid, alternating amber and gold fill, simple and bold, centered on white',
    settings: { ...D, numColors: 3 }, // black outline, amber, gold
  },
  {
    id: 'star-burst',
    name: 'Eight-Pointed Star',
    category: 'geometric',
    description: 'Classic eight-pointed star with radiating points',
    prompt: 'a bold perfectly eight-fold radially symmetric eight-pointed star with identical alternating long and short points in deep teal and cream, centered on white',
    settings: { ...D, numColors: 3 }, // black, deep teal, cream
  },
  {
    id: 'celtic-knot',
    name: 'Celtic Knot',
    category: 'geometric',
    description: 'Interlaced Celtic trinity knot in forest green',
    prompt: 'a Celtic trinity knot in a perfect circle with three identical interlaced bands of equal width in forest green with a thin gold outline, three-fold radially symmetric, centered on white',
    settings: { ...D, numColors: 3 }, // black, forest green, gold outline
  },
  {
    id: 'diamond-grid',
    name: 'Diamond Lattice',
    category: 'geometric',
    description: 'Repeating diamond lattice in navy and white',
    prompt: 'a perfectly repeating diamond lattice pattern of uniform identical diamonds in navy blue and white with small gold dot accents at every intersection, centered on white',
    settings: { ...D, numColors: 3 }, // navy, white, gold dots
  },
  {
    id: 'pinwheel',
    name: 'Pinwheel',
    category: 'geometric',
    description: 'Four-blade pinwheel in bright primary colours',
    prompt: 'a four-blade pinwheel with four identical blades of equal size alternating red and blue arranged with perfect four-fold rotational symmetry around a yellow circular centre, centered on white',
    settings: { ...D, numColors: 4 }, // black, red, blue, yellow
  },
  {
    id: 'compass-rose',
    name: 'Compass Rose',
    category: 'geometric',
    description: 'Nautical compass rose in navy and gold',
    prompt: 'a nautical compass rose with sixteen identical sharp points arranged with perfect sixteen-fold radial symmetry alternating navy blue and gold, centered on white',
    settings: { ...D, numColors: 3 }, // black, navy, gold
  },
];

/** Look up catalog entry by id */
export function getCatalogEntry(id) {
  return CATALOG.find(e => e.id === id) ?? null;
}
