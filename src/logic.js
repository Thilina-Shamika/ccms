var LF_VERTEX = `#version 300 es
in vec2 aPosition;
void main() {
  gl_Position = vec4(aPosition, 0.0, 1.0);
}`;

var LF_FRAGMENT = `#version 300 es
precision highp float;
out vec4 outColor;
uniform vec2 uResolution;
uniform float uDpr;
uniform float uScale;
uniform float uTime;
uniform float uBeamX;
uniform vec4 uSurface;
uniform float uRadius;
uniform vec3 uIntro;
uniform vec4 uPour;
uniform vec2 uRun;
uniform vec4 uLens;
uniform sampler2D uReveal;
uniform vec4 uRevealMap;
uniform vec2 uRevealInfo;
uniform float uAtmosphere;
uniform vec4 uAmount;
uniform vec4 uShape;
uniform vec4 uExtra;
uniform float uTheme;
uniform vec3 uTint[16];
uniform float uClouds;

#define BEAM uTint[0]
#define LEFT uTint[1]
#define RIGHT uTint[2]
#define CYAN uTint[3]
#define PINK uTint[4]
#define LILAC uTint[5]
#define SKY uTint[6]
#define PURPLE uTint[7]
#define DEEP uTint[8]
#define MIST uTint[9]
#define NAVY uTint[10]
#define WARM uTint[11]
#define EMBER uTint[12]
#define WHITE uTint[13]
#define HAZE uTint[14]
#define LAVENDER uTint[15]

float hash(vec2 p) {
  p = fract(p * vec2(123.34, 456.21));
  p += dot(p, p + 45.32);
  return fract(p.x * p.y);
}

float noise(vec2 p) {
  vec2 i = floor(p);
  vec2 f = fract(p);
  vec2 u = f * f * (3.0 - 2.0 * f);
  return mix(mix(hash(i), hash(i + vec2(1.0, 0.0)), u.x), mix(hash(i + vec2(0.0, 1.0)), hash(i + vec2(1.0, 1.0)), u.x), u.y);
}

float fbm(vec2 p) {
  float v = 0.0;
  float a = 0.5;
  mat2 m = mat2(1.6, 1.2, -1.2, 1.6);
  for (int i = 0; i < 5; i++) {
    v += a * noise(p);
    p = m * p;
    a *= 0.5;
  }
  return v;
}

float sq(float x) {
  return x * x;
}

float roundBox(vec2 p, vec2 b, float r) {
  vec2 q = abs(p) - b + r;
  return length(max(q, 0.0)) + min(max(q.x, q.y), 0.0) - r;
}

vec3 spill(float e, float fall, float strength, float front, float t, out vec3 glow) {
  glow = vec3(0.0);
  if (strength < 0.0005) return vec3(0.0);
  float f = max(fall, 0.0);
  float d = max(e, 0.0);
  float u = d / (6.0 + 0.28 * f);
  float start = smoothstep(-6.0, 12.0, fall);
  float fade = exp(-sq(max(f - 125.0, 0.0) / 40.0));
  float streak = 0.88 + 0.24 * noise(vec2(u * 6.0, f / 22.0 - t * 1.7));
  float bright = pow(strength, 1.5);
  float soft = sqrt(strength);
  float warmth = smoothstep(90.0, 130.0, f);
  vec3 coreK = mix(WHITE, WARM, warmth * exp(-d / 9.0));
  float core = mix(9.0, 2.6, warmth) * exp(-sq(d / (3.5 + 0.04 * f))) * exp(-sq(max(f - 130.0, 0.0) / 38.0));
  float wall = 24.0 * exp(-sq(d / 1.1)) * exp(-sq(max(f - 100.0, 0.0) / 30.0));
  float bandCenter = 0.7 - 0.3 * smoothstep(30.0, 110.0, f);
  float offset = u - bandCenter;
  float decay = (1.05 - bandCenter) / 1.31;
  float profile = offset < 0.0 ? exp(-sq(offset / 0.3)) : exp(-offset / decay);
  profile *= 1.0 - smoothstep(1.0, 1.4, u);
  vec3 bandA = mix(CYAN, PINK, smoothstep(50.0, 75.0, f));
  bandA = mix(bandA, LILAC, smoothstep(100.0, 125.0, f));
  vec3 bandB = mix(SKY, PURPLE, smoothstep(50.0, 75.0, f));
  vec3 fanK = mix(bandA, bandB, smoothstep(0.06, 0.18, offset));
  fanK = mix(fanK, DEEP, smoothstep(0.22, 0.42, offset));
  vec3 thread = WHITE * wall * bright + coreK * core * streak * bright;
  glow += fanK * 4.5 * profile * fade * streak * bright;
  glow += MIST * 0.7 * exp(-max(u - 1.0, 0.0) / 0.9) * smoothstep(0.7, 1.2, u) * fade * soft;
  glow += EMBER * 0.35 * exp(-sq((f - 165.0) / 22.0)) * exp(-d / 25.0) * bright;
  float lag = u * (6.0 + 0.28 * f) * 0.35;
  float reveal = 1.0 - smoothstep(front - 70.0, front + 8.0, f + lag);
  glow *= start * reveal;
  return thread * start * reveal;
}

vec3 easeLight(vec3 light, float amount) {
  return -log(max(1.0 - amount * (1.0 - exp(-light)), vec3(0.0001)));
}

void main() {
  vec2 frag = vec2(gl_FragCoord.x, uResolution.y * uDpr - gl_FragCoord.y) / uDpr;
  vec2 p = frag / uScale;
  float t = uTime;
  float bx = uBeamX / uScale;
  float sl = uSurface.x / uScale;
  float sy = uSurface.y / uScale;
  float sr = uSurface.z / uScale;
  float sb = uSurface.w / uScale;
  float radius = uRadius / uScale;
  float dx = p.x - bx;
  float adx = abs(dx);
  float h = sy - p.y;
  float hp = max(h, 0.0);
  float above = smoothstep(-0.5, 0.5, h);
  float side = smoothstep(-24.0, 24.0, dx);
  vec3 sideK = mix(mix(LAVENDER, LEFT, smoothstep(40.0, 140.0, adx)), RIGHT, side);
  float beamWidth = uShape.x;
  float flare = uShape.y;
  float spread = 250.0 * uShape.z;
  float reachL = max(bx - sl, 1.0);
  float reachR = max(sr - bx, 1.0);
  float reach = dx < 0.0 ? reachL : reachR;
  float layerLen = clamp(0.29 * reach, 20.0, 100.0) * sqrt(uShape.z);
  float run = uRun.x;
  float runMask = 1.0 - smoothstep(run - 34.0, run + 6.0, adx);
  float bead = exp(-sq((adx - run + 16.0) / (18.0 + 0.04 * run))) * uRun.y;
  float flowMask = (1.0 - smoothstep(0.75 * spread, 1.1 * spread, adx)) * runMask;
  float edgeMask = (1.0 - smoothstep(0.8 * spread, 1.25 * spread, adx)) * runMask;
  float bloom = uIntro.y;
  vec2 center = vec2((sl + sr) * 0.5, (sy + sb) * 0.5);
  vec2 halfSize = vec2((sr - sl) * 0.5, (sb - sy) * 0.5);
  float sd = roundBox(p - center, halfSize, radius);
  float outline = max(sd, 0.0);
  float below = max(p.y - sy - radius, 0.0);
  float hug = smoothstep(-0.5, 0.5, sd) * exp(-sq(below / 14.0));
  float hugWide = smoothstep(-0.5, 0.5, sd) * exp(-sq(below / 40.0));

  vec3 col = vec3(0.0);

  float breathe = 1.0 + uExtra.x * (0.12 * sin(t * 1.5708) + 0.08 * (noise(vec2(t * 0.5, 3.0)) - 0.5));

  float front = uIntro.x / uScale;
  float drop = smoothstep(front + 10.0, front - 110.0, p.y);
  float falling = 1.0 - smoothstep(sy - 24.0, sy, front);
  float top = mix(0.3, 1.0, smoothstep(0.0, 0.3 * sy, p.y));
  float beamCore = 24.0 * exp(-adx / (2.0 * beamWidth));
  float beamHalo = 1.3 * exp(-adx / (6.0 * beamWidth)) + 0.3 * exp(-adx / (22.0 * beamWidth));
  vec3 haloK = mix(BEAM, sideK, exp(-hp / 80.0));
  col += (BEAM * beamCore + haloK * beamHalo) * top * above * drop;
  float head = exp(-sq((p.y - front) / 24.0)) * falling;
  col += mix(WHITE, BEAM, 0.35) * head * (7.0 * exp(-adx / (2.6 * beamWidth)) + 1.0 * exp(-adx / (14.0 * beamWidth)));

  float psi = adx * (outline + 1.0);
  float rise = max(hp - 17.9 * flare, 0.0);
  float skirtAmp = 16.6 * (exp(-sq(rise / (11.8 * flare))) + 0.3 * exp(-rise / (60.0 * flare)));
  float skirtSpread = mix(134.0, 155.0, side) * breathe * flare * flare * mix(0.35, 1.0, min(bloom, 1.0)) * max(bloom, 1.0);
  float skirt = skirtAmp * exp(-psi / skirtSpread) * exp(-sq(adx / (max(layerLen, 60.0 * sqrt(uShape.z)) * 1.48))) * hug;
  col += sideK * skirt * flowMask * min(bloom, 1.0);

  float layer = 12.0 * exp(-adx / layerLen) * exp(-outline / (0.19 * layerLen)) * (1.0 + 0.4 * bead);
  col += sideK * layer * hug * flowMask * min(bloom, 1.0);
  float washMask = smoothstep(sl - 60.0, sl + 6.0, p.x) * (1.0 - smoothstep(sr - 6.0, sr + 45.0, p.x));
  float wash = 1.4 * exp(-adx / 100.0) * exp(-outline / 30.0);
  col += mix(BEAM, sideK, 0.25) * wash * hugWide * washMask * flowMask * min(bloom, 1.0);
  float highWash = 0.7 * exp(-adx / 140.0) * exp(-outline / 60.0);
  col += mix(BEAM, NAVY, 0.5) * highWash * hugWide * washMask * runMask * min(bloom, 1.0);

  float sideSign = dx < 0.0 ? 0.0 : 1.0;
  float along = 0.5 * log((hp + 1.0) / (adx + 1.0));
  float lineScale = 6.0;
  float lp = log(max(psi, 1.0) / (120.0 * flare * flare)) * lineScale;
  float lineIndex = floor(lp) + sideSign * 97.0;
  float wobble = 0.22 * (noise(vec2(lineIndex * 3.7, t * 0.4 + along)) - 0.5);
  float lf = fract(lp + wobble) - 0.5;
  float gradient = lineScale * length(vec2(hp + 1.0, adx)) / max(psi, 1.0) / uScale;
  float halfWidth = max(0.35 * gradient, 0.0001);
  float drawWidth = max(halfWidth, 0.6 * gradient);
  float lineShape = exp(-lf * lf / (drawWidth * drawWidth)) * (halfWidth / drawWidth);
  float lineOn = step(0.3, hash(vec2(lineIndex, 1.3)));
  float lineFlow = smoothstep(0.25, 0.85, noise(vec2(lineIndex * 5.3 + 2.0, along * 3.0 + t * 1.1)));
  float flareArea = 120.0 * flare * flare;
  float lineEnvelope = smoothstep(0.85 * flareArea, 1.4 * flareArea, psi) * (1.0 - smoothstep(3.2 * flareArea, 7.5 * flareArea, psi));
  lineEnvelope *= exp(-adx / (layerLen * 1.5)) * hug * flowMask * (1.0 - smoothstep(35.0 * flare, 80.0 * flare, hp));
  float lineBright = mix(0.35, 1.0, hash(vec2(lineIndex, 4.0)));
  col += mix(sideK, WHITE, 0.6) * lineShape * lineOn * lineFlow * lineEnvelope * lineBright * 2.6 * uAmount.w * min(bloom, 1.0);

  float edgeGlow = 22.8 * exp(-sq(adx / (150.0 * uShape.z))) * edgeMask * (1.0 + 0.9 * bead);
  float onTop = 1.0 - smoothstep(sy + radius, sy + radius + 10.0, p.y);
  float edgeLine = (exp(-sq(max(sd, 0.0) / 0.9)) + 0.12 * exp(-max(sd, 0.0) / 3.0)) * edgeGlow * onTop;
  col += mix(sideK, WHITE, 0.6) * edgeLine * min(bloom, 1.0);

  float pour = uShape.w;
  float baseline = exp(-sq(130.0 / 150.0));
  float strengthR = exp(-sq(reachR / (150.0 * uShape.z))) * (1.0 - smoothstep(0.8 * spread, 1.25 * spread, reachR)) / baseline * pour;
  float strengthL = exp(-sq(reachL / (150.0 * uShape.z))) * (1.0 - smoothstep(0.8 * spread, 1.25 * spread, reachL)) / baseline * pour;
  float fallY = p.y - sy - 0.3 * radius;
  float rightHalf = smoothstep(center.x - 4.0, center.x + 4.0, p.x);
  float haloR = exp(-length(p - vec2(sr - 0.3 * radius, sy + 0.3 * radius)) / 40.0) * sqrt(strengthR);
  float haloL = exp(-length(p - vec2(sl + 0.3 * radius, sy + 0.3 * radius)) / 40.0) * sqrt(strengthL);
  vec3 glowR;
  vec3 glowL;
  col += spill(sd, fallY, strengthR, uPour.y, t, glowR) * rightHalf;
  col += spill(sd, fallY, strengthL, uPour.x, t, glowL) * (1.0 - rightHalf);
  col += easeLight(glowR * rightHalf + NAVY * 0.9 * haloR, uPour.w);
  col += easeLight(glowL * (1.0 - rightHalf) + NAVY * 0.9 * haloL, uPour.z);

  vec2 toLens = frag - uLens.xy;
  float lens = exp(-dot(toLens, toLens) / sq(uLens.z)) * uLens.w;
  col *= 1.0 + 0.35 * lens * hug;
  /* Clouds-only mode (pages other than home): drop the beam and its landing glow, keep the drifting fog */
  col *= 1.0 - uClouds;
  float fogAmount = uAmount.y * uAtmosphere;
  float near = exp(-adx / 150.0);
  float envelope = near * (0.3 + 0.4 * exp(-hp / 50.0) + 1.2 * exp(-p.y / 120.0));
  envelope = mix(envelope, 0.1 + 0.6 * exp(-hp / 240.0), uClouds);
  if (fogAmount > 0.001 && h > -2.0 && envelope * max(0.25, 6.0 * exp(-adx / 50.0)) > 0.002) {
    vec2 fq = vec2(dx / 1.7, h) / 85.0 + vec2(t * 0.012, -t * 0.03) + uExtra.zw;
    vec2 fw = vec2(fbm(fq * 1.3 + vec2(1.7, 9.2) + t * 0.03), fbm(fq * 1.3 + vec2(8.3, 2.8) - t * 0.025));
    float cloud = fbm(fq + 1.4 * fw);
    float density = smoothstep(0.5, 0.78, cloud);
    float lit = exp(-adx / 50.0);
    float fogMask = smoothstep(-2.0, 20.0, h);
    float reached = smoothstep(front + 80.0, front - 40.0, p.y);
    vec3 fog = (HAZE * 0.45 + BEAM * 6.0 * lit * reached * (1.0 - uClouds) + mix(LAVENDER, BEAM, 0.55) * 0.9 * uClouds) * density * envelope * fogMask;
    float surfaceLit = exp(-adx / (layerLen * 1.3)) * exp(-outline / 28.0) * hugWide * flowMask * washMask * min(bloom, 1.0);
    fog += sideK * 2.2 * surfaceLit * (smoothstep(0.38, 0.72, cloud) - 0.35) * fogMask * (1.0 - uClouds);
    float smoke = smoothstep(0.3, 0.75, cloud);
    fog += BEAM * 0.35 * exp(-adx / (22.0 * beamWidth)) * (0.35 + 0.9 * smoke) * fogMask * top * drop * (1.0 - uClouds);
    col += fog * fogAmount * (1.0 + 1.2 * lens) * mix(1.0, 0.45, uTheme);
  }

  if (uRevealInfo.y > 0.001 && uLens.w > 0.002) {
    vec2 toReveal = frag - uLens.xy;
    float reveal = exp(-dot(toReveal, toReveal) / sq(uRevealInfo.x)) * uLens.w;
    vec2 uv = frag * uRevealMap.xy + uRevealMap.zw;
    float onImage = step(0.0, uv.x) * step(uv.x, 1.0) * step(0.0, uv.y) * step(uv.y, 1.0);
    vec4 ui = texture(uReveal, uv);
    float ink = max(ui.r, max(ui.g, ui.b)) * onImage;
    float lit = clamp(col.b * 0.9, 0.0, 1.0) * (1.0 - smoothstep(0.9, 2.2, col.b));
    float clearance = smoothstep(60.0 * sqrt(beamWidth), 150.0 * sqrt(beamWidth), adx);
    col += mix(BEAM, WHITE, 0.4) * ink * reveal * lit * clearance * uRevealInfo.y * 2.2;
  }

  float haze = col.b;
  float dotGrid = 1.0 - smoothstep(0.16, 0.32, length(fract(frag / 3.0) - 0.5));
  col += BEAM * dotGrid * clamp(haze, 0.0, 1.5) * (1.0 - smoothstep(1.5, 4.0, haze)) * (0.18 + 0.3 * lens) * uExtra.y;
  if (lens > 0.002) {
    vec2 drift = frag - vec2(0.0, t * 14.0);
    vec2 sparkCell = floor(drift / 7.0);
    vec2 sparkPos = (sparkCell + 0.2 + 0.6 * vec2(hash(sparkCell + 5.1), hash(sparkCell + 2.3))) * 7.0;
    float sparkDist = length(drift - sparkPos);
    float sparkOn = step(0.8, hash(sparkCell + 8.8));
    float sparkTwinkle = 0.5 + 0.5 * sin(t * 5.0 + hash(sparkCell + 3.7) * 6.283);
    col += WHITE * exp(-sparkDist * sparkDist / 0.35) * sparkOn * sparkTwinkle * lens * clamp(haze * 1.5, 0.0, 1.0) * 1.6 * uAmount.z;
  }

  float dustAmount = uAmount.z;
  if (dustAmount > 0.001 && uClouds < 0.5) {
    float dustLp = log(max(psi, 1.0) / (120.0 * flare * flare)) * 2.2;
    vec2 flowCell = vec2(dustLp / 1.1, (along + t * 0.22) / 0.06);
    vec2 cellId = floor(flowCell) + vec2(sideSign * 131.0, 0.0);
    vec2 cellJitter = vec2(hash(cellId + 1.7), hash(cellId + 8.3));
    vec2 particleFlow = (floor(flowCell) + 0.1 + cellJitter * 0.8) * vec2(1.1, 0.06);
    float particlePsi = 120.0 * flare * flare * exp(particleFlow.x / 2.2);
    float particleAlong = particleFlow.y - t * 0.22;
    float particleX = sqrt(particlePsi * exp(-2.0 * particleAlong)) - 1.0;
    float particleH = sqrt(particlePsi * exp(2.0 * particleAlong)) - 1.0;
    float particleDist = length(vec2(adx - particleX, hp - particleH)) * uScale;
    float particleOn = step(0.62, hash(cellId + 3.1));
    float particleTwinkle = 0.5 + 0.5 * sin(t * 5.0 + hash(cellId + 9.2) * 6.283);
    float dustZone = exp(-sq(log(max(psi, 1.0) / (200.0 * flare * flare)) / 0.55)) * hug * flowMask * smoothstep(0.0, 6.0, outline);
    col += WHITE * exp(-particleDist * particleDist / 0.3) * particleOn * particleTwinkle * dustZone * 3.0 * dustAmount * min(bloom, 1.0);

    vec2 glitterCell = vec2(dx / 3.0, (p.y - t * 26.0) / 9.0);
    vec2 glitterId = floor(glitterCell);
    vec2 glitterJitter = vec2(hash(glitterId + 4.4), hash(glitterId + 2.9));
    vec2 glitterPos = (glitterId + 0.15 + glitterJitter * 0.7) * vec2(3.0, 9.0);
    float glitterDist = length(vec2(dx, p.y - t * 26.0) - glitterPos) * uScale;
    float glitterOn = step(0.7, hash(glitterId + 6.6));
    float glitterTwinkle = 0.5 + 0.5 * sin(t * 6.0 + hash(glitterId + 1.1) * 6.283);
    float glitterZone = exp(-adx / (5.0 * beamWidth)) * smoothstep(1.5, 4.0, adx / beamWidth) * above * smoothstep(25.0, 70.0, hp) * top * drop;
    col += WHITE * exp(-glitterDist * glitterDist / 0.25) * glitterOn * glitterTwinkle * glitterZone * 2.2 * dustAmount * uAtmosphere;
  }

  col *= uAmount.x * (1.0 + uIntro.z * 0.9 * exp(-length(vec2(dx, h * 1.6)) / 70.0));
  col *= smoothstep(-0.75, 0.25, sd * uScale);

  vec3 emit = 1.0 - exp(-col * mix(1.0, 0.6, uTheme));
  float peak = max(emit.r, max(emit.g, emit.b));
  if (uTheme > 0.5) {
    float low = min(emit.r, min(emit.g, emit.b));
    float chroma = peak - low;
    vec3 hue = (emit - low) / max(chroma, 0.0001);
    float alpha = clamp(pow(chroma, 1.35) * 1.3, 0.0, 1.0) * 0.9;
    outColor = vec4((hue * 0.82 + 0.06) * alpha, alpha);
  } else {
    outColor = vec4(emit, peak);
  }
}`;

var LF_TINTS = [[0, 1], [-11.5, 0.77], [9.5, 0.95], [-53.5, 0.79], [39.5, 0.77], [16, 0.81], [-16.3, 0.92], [13.3, 0.96], [3, 1.01], [1, 0.68], [1, 1.15], [142.5, 0.51], [113.6, 0.28], [-7.5, 0.13], [-2.7, 0.32], [7.5, 0.81]];

function lfClamp(v, a, b) { return Math.min(b, Math.max(a, v)); }
function lfEaseOut(x) { return 1 - Math.pow(1 - lfClamp(x, 0, 1), 3); }
function lfSpring(time) {
  var omega = 8, zeta = 0.62, damped = omega * Math.sqrt(1 - zeta * zeta);
  return 1 - Math.exp(-zeta * omega * time) * (Math.cos(damped * time) + ((zeta * omega) / damped) * Math.sin(damped * time));
}
function lfToHsv(c) {
  var r = c[0], g = c[1], b = c[2];
  var max = Math.max(r, g, b), min = Math.min(r, g, b), delta = max - min, hue = 0;
  if (delta > 0) {
    if (max === r) hue = ((g - b) / delta) % 6;
    else if (max === g) hue = (b - r) / delta + 2;
    else hue = (r - g) / delta + 4;
  }
  return [(hue * 60 + 360) % 360, max > 0 ? delta / max : 0];
}
function lfFromHsv(hue, saturation) {
  var h = (((hue % 360) + 360) % 360) / 60, c = saturation, x = c * (1 - Math.abs((h % 2) - 1)), m = 1 - c, v;
  v = h < 1 ? [c, x, 0] : h < 2 ? [x, c, 0] : h < 3 ? [0, c, x] : h < 4 ? [0, x, c] : h < 5 ? [x, 0, c] : [c, 0, x];
  return [v[0] + m, v[1] + m, v[2] + m];
}
function lfBuildTints(rgb) {
  var hs = lfToHsv(rgb), strength = hs[1] / 0.78, data = new Float32Array(LF_TINTS.length * 3);
  LF_TINTS.forEach(function (t, i) { data.set(lfFromHsv(hs[0] + t[0], lfClamp(0.78 * t[1] * strength, 0, 1)), i * 3); });
  return data;
}
function lfHexToRgb(hex) {
  var m = /^#?([0-9a-f]{6})$/i.exec(String(hex || '').trim());
  var x = m ? parseInt(m[1], 16) : 0x3847ff;
  return [((x >> 16) & 255) / 255, ((x >> 8) & 255) / 255, (x & 255) / 255];
}

function lfHex(h) { var x = parseInt(h.slice(1), 16); return [((x >> 16) & 255) / 255, ((x >> 8) & 255) / 255, (x & 255) / 255]; }
/* Aurora palettes for the 16 tint slots: BEAM, LEFT, RIGHT, CYAN, PINK, LILAC, SKY, PURPLE, DEEP, MIST, NAVY, WARM, EMBER, WHITE, HAZE, LAVENDER */
var LF_AURORA_A = ['#6FF7D2', '#2EE6A6', '#8B7CFF', '#22D3EE', '#E879F9', '#C4B5FD', '#38BDF8', '#8B5CF6', '#4338CA', '#5EEAD4', '#1E3A8A', '#A7F3D0', '#34D399', '#86EFD6', '#0F766E', '#A5B4FC'].map(lfHex);
var LF_AURORA_B = ['#9C8CFF', '#38E1C6', '#C084FC', '#67E8F9', '#F472B6', '#DDD6FE', '#60A5FA', '#A855F7', '#5B21B6', '#99F6E4', '#312E81', '#BAE6FD', '#2DD4BF', '#BBA9FF', '#4C1D95', '#C7D2FE'].map(lfHex);
function lfAurora(t) {
  var m = 0.5 + 0.5 * Math.sin(t * 0.12), out = new Float32Array(48);
  for (var i = 0; i < 16; i++) for (var c = 0; c < 3; c++) out[i * 3 + c] = LF_AURORA_A[i][c] * (1 - m) + LF_AURORA_B[i][c] * m;
  return out;
}

/* Faithful port of React Bits <LaserFlow> (no reveal image). */
function createLaserFlow(container, canvas, getSurface, getSettings) {
  var gl = canvas.getContext('webgl2', { alpha: true, premultipliedAlpha: true, antialias: false, depth: false, stencil: false });
  if (!gl) return null;
  function compile(type, src) {
    var s = gl.createShader(type); gl.shaderSource(s, src); gl.compileShader(s);
    if (gl.getShaderParameter(s, gl.COMPILE_STATUS)) return s;
    gl.deleteShader(s); return null;
  }
  var vsh = compile(gl.VERTEX_SHADER, LF_VERTEX), fsh = compile(gl.FRAGMENT_SHADER, LF_FRAGMENT);
  if (!vsh || !fsh) return null;
  var program = gl.createProgram();
  gl.attachShader(program, vsh); gl.attachShader(program, fsh); gl.linkProgram(program);
  if (!gl.getProgramParameter(program, gl.LINK_STATUS)) return null;
  var names = ['uResolution','uDpr','uScale','uTime','uBeamX','uSurface','uRadius','uIntro','uPour','uRun','uLens','uReveal','uRevealMap','uRevealInfo','uAtmosphere','uAmount','uShape','uExtra','uTheme','uTint','uClouds'];
  var U = {}; names.forEach(function (n) { U[n] = gl.getUniformLocation(program, n); });
  var vao = gl.createVertexArray(), buffer = gl.createBuffer();
  gl.bindVertexArray(vao); gl.bindBuffer(gl.ARRAY_BUFFER, buffer);
  gl.bufferData(gl.ARRAY_BUFFER, new Float32Array([-1, -1, 3, -1, -1, 3]), gl.STATIC_DRAW);
  var pos = gl.getAttribLocation(program, 'aPosition');
  gl.enableVertexAttribArray(pos); gl.vertexAttribPointer(pos, 2, gl.FLOAT, false, 0, 0);
  gl.bindVertexArray(null);
  var tex = gl.createTexture();
  gl.bindTexture(gl.TEXTURE_2D, tex);
  gl.texImage2D(gl.TEXTURE_2D, 0, gl.RGBA, 1, 1, 0, gl.RGBA, gl.UNSIGNED_BYTE, new Uint8Array([0, 0, 0, 0]));

  var reduce = window.matchMedia ? window.matchMedia('(prefers-reduced-motion: reduce)').matches : false;
  var st = {
    time: 0, introTime: (getSettings().intro && !reduce) ? 0 : 5,
    width: 1, height: 1, ratio: 1, colorKey: '', tints: lfBuildTints([0.22, 0.28, 1]),
    pointer: { x: 0, y: 0, inside: false }, lens: { x: 0, y: 0, vx: 0, vy: 0, strength: 0, placed: false }
  };
  var raf = 0, last = 0, visible = true, alive = true;

  function viewScale() {
    var b = container.getBoundingClientRect();
    var k = container.clientWidth ? b.width / container.clientWidth : 1;
    return k > 0 ? k : 1;
  }
  function measure(width, height, s) {
    var el = getSurface();
    if (el) {
      var k = viewScale();
      var box = container.getBoundingClientRect(), r = el.getBoundingClientRect();
      if (r.width > 0) {
        var cs = getComputedStyle(el);
        var rad = Math.max(parseFloat(cs.borderTopLeftRadius) || 0, parseFloat(cs.borderTopRightRadius) || 0);
        var w = r.width / k, h = r.height / k;
        return { left: (r.left - box.left) / k, top: (r.top - box.top) / k, right: (r.right - box.left) / k, bottom: (r.bottom - box.top) / k, radius: Math.min(rad, w / 2, h / 2), real: true };
      }
    }
    return { left: -width * 2, top: s.surfaceLevel * height, right: width * 3, bottom: height * 3, radius: 0, real: false };
  }
  function resize() {
    var width = Math.max(1, container.clientWidth), height = Math.max(1, container.clientHeight);
    var baseDpr = Math.min(window.devicePixelRatio || 1, 2);
    var longest = Math.max(width, height) * baseDpr;
    var ratio = longest > 2048 ? (baseDpr * 2048) / longest : baseDpr;
    var pw = Math.max(1, Math.round(width * ratio)), ph = Math.max(1, Math.round(height * ratio));
    if (canvas.width !== pw || canvas.height !== ph) { canvas.width = pw; canvas.height = ph; }
    st.width = width; st.height = height; st.ratio = canvas.width / width;
    render();
  }
  function render() {
    var s = getSettings();
    if (s.palette === 'aurora') { st.tints = lfAurora(st.time); st.colorKey = 'aurora'; }
    else if (s.color !== st.colorKey) { st.colorKey = s.color; st.tints = lfBuildTints(lfHexToRgb(s.color)); }
    var width = st.width, height = st.height;
    var scale = Math.max(0.2, Math.min(width / 585, height / 507));
    var surface = measure(width, height, s);
    var beamX = s.beamPosition * width;
    if (surface.real) {
      var margin = surface.radius + 6;
      if (beamX >= surface.left && beamX <= surface.right) beamX = lfClamp(beamX, surface.left + margin, surface.right - margin);
      else surface = { left: -width * 2, top: height, right: width * 3, bottom: height * 3, radius: 0, real: false };
    }
    var startY = -0.15 * height, span = surface.top - startY + 0.3 * height, it = st.introTime, settled = it >= 5;
    var front = settled ? surface.top + 0.3 * height : startY + span * Math.pow(lfClamp(it / 1.25, 0, 1), 1.3);
    var impact = 1.25 * Math.pow(Math.max(0, surface.top - startY) / span, 1 / 1.3);
    var tau = it - impact;
    var bloom = settled ? 1 : tau <= 0 ? 0 : lfSpring(tau);
    var flash = settled || tau <= 0 ? 0 : Math.exp(-tau / 0.35) * (1 - Math.exp(-tau / 0.05));
    var runRange = s.spread * 250 * 1.3 + 80;
    var runFront = settled ? 100000 : tau <= 0 ? -40 : runRange * (1 - Math.exp(-1.15 * tau));
    var beadStrength = settled || tau <= 0 ? 0 : Math.exp(-1.15 * tau) * (1 - Math.exp(-tau / 0.08));
    function pour(reach) {
      if (settled) return [1000, 1];
      if (tau <= 0) return [-reach, 0];
      var target = Math.min(reach, runRange * 0.97);
      var arrival = -Math.log(1 - target / runRange) / 1.15;
      var elapsed = tau - arrival;
      var ease = lfClamp((elapsed + 0.15) / 0.8, 0, 1);
      var fill = ease * ease * ease * (ease * (ease * 6 - 15) + 10);
      if (elapsed <= 0) return [runFront - target, fill];
      var speed = 1.15 * (runRange - target);
      return [speed * elapsed + 260 * elapsed * elapsed, fill];
    }
    var pl = pour((beamX - surface.left) / scale), pr = pour((surface.right - beamX) / scale);
    var atmosphere = settled ? 1 : tau <= 0 ? 0.3 * lfEaseOut(it / 1.25) : 0.3 + 0.7 * (1 - Math.exp(-1.3 * tau));
    var seed = Number(s.seed) || 0;

    gl.viewport(0, 0, canvas.width, canvas.height);
    gl.clearColor(0, 0, 0, 0); gl.clear(gl.COLOR_BUFFER_BIT);
    gl.useProgram(program);
    gl.uniform2f(U.uResolution, width, height);
    gl.uniform1f(U.uDpr, st.ratio);
    gl.uniform1f(U.uScale, scale);
    gl.uniform1f(U.uTime, st.time);
    gl.uniform1f(U.uBeamX, beamX);
    gl.uniform4f(U.uSurface, surface.left, surface.top, surface.right, surface.bottom);
    gl.uniform1f(U.uRadius, surface.radius);
    gl.uniform3f(U.uIntro, front, bloom, flash);
    gl.uniform4f(U.uPour, pl[0], pr[0], pl[1], pr[1]);
    gl.uniform2f(U.uRun, runFront, beadStrength);
    gl.uniform4f(U.uLens, st.lens.x, st.lens.y, 95 * scale, st.lens.strength);
    gl.activeTexture(gl.TEXTURE0); gl.bindTexture(gl.TEXTURE_2D, tex); gl.uniform1i(U.uReveal, 0);
    gl.uniform4f(U.uRevealMap, 1, 1, 0, 0);
    gl.uniform2f(U.uRevealInfo, 220, 0);
    gl.uniform1f(U.uAtmosphere, atmosphere);
    gl.uniform4f(U.uAmount, s.intensity, s.fog, s.dust, s.streaks);
    gl.uniform4f(U.uShape, s.beamWidth, s.flare, s.spread, s.spill);
    gl.uniform4f(U.uExtra, s.pulse, s.dots, 34.34 + seed * 7.31, 11.58 + seed * 3.17);
    gl.uniform1f(U.uTheme, 0);
    gl.uniform1f(U.uClouds, s.clouds ? 1 : 0);
    gl.uniform3fv(U.uTint, st.tints);
    gl.bindVertexArray(vao); gl.drawArrays(gl.TRIANGLES, 0, 3); gl.bindVertexArray(null);
  }
  function frame(now) {
    raf = 0;
    if (!alive || !visible || document.hidden) return;
    var s = getSettings();
    var dt = last ? Math.min(0.05, (now - last) / 1000) : 1 / 60;
    last = now;
    var moving = !reduce && s.speed > 0;
    if (moving) st.time += dt * s.speed;
    var introducing = st.introTime < 5;
    if (introducing) st.introTime = Math.min(5, st.introTime + dt);
    var p = st.pointer, l = st.lens, active = s.mouseInteraction && p.inside && !reduce;
    if (active && !l.placed) { l.x = p.x; l.y = p.y; l.vx = 0; l.vy = 0; l.placed = true; }
    var ax = 120 * (p.x - l.x) - 19 * l.vx, ay = 120 * (p.y - l.y) - 19 * l.vy;
    l.vx += ax * dt; l.vy += ay * dt; l.x += l.vx * dt; l.y += l.vy * dt;
    var goal = active ? 1 : 0;
    l.strength += (goal - l.strength) * (1 - Math.exp(-dt / (goal > l.strength ? 0.3 : 0.55)));
    if (l.strength < 0.001 && !active) l.placed = false;
    render();
    var settling = Math.abs(l.strength - goal) > 0.002 || Math.hypot(l.vx, l.vy) > 0.5;
    if (moving || introducing || settling) raf = requestAnimationFrame(frame); else last = 0;
  }
  function wake() { if (!raf && alive && visible && !document.hidden) raf = requestAnimationFrame(frame); }
  function onMove(e) {
    var r = container.getBoundingClientRect(), k = viewScale();
    var x = (e.clientX - r.left) / k, y = (e.clientY - r.top) / k;
    st.pointer.x = x; st.pointer.y = y;
    st.pointer.inside = x >= 0 && y >= 0 && x <= container.clientWidth && y <= container.clientHeight;
    wake();
  }
  function onLeave() { st.pointer.inside = false; wake(); }
  function onVis() { last = 0; wake(); }
  var ro = new ResizeObserver(resize);
  ro.observe(container);
  var surf = getSurface(); if (surf) ro.observe(surf);
  var io = new IntersectionObserver(function (entries) {
    visible = entries.some(function (e) { return e.isIntersecting; });
    if (visible) { last = 0; wake(); }
  });
  io.observe(container);
  window.addEventListener('pointermove', onMove, { passive: true });
  document.documentElement.addEventListener('pointerleave', onLeave);
  document.addEventListener('visibilitychange', onVis);
  resize(); wake();
  return {
    wake: function () { if (!raf) render(); wake(); },
    destroy: function () {
      alive = false; cancelAnimationFrame(raf); ro.disconnect(); io.disconnect();
      window.removeEventListener('pointermove', onMove);
      document.documentElement.removeEventListener('pointerleave', onLeave);
      document.removeEventListener('visibilitychange', onVis);
      gl.deleteTexture(tex); gl.deleteBuffer(buffer); gl.deleteVertexArray(vao); gl.deleteProgram(program);
    }
  };
}

var CCMS_INDUSTRIES = [
  { label: 'Healthcare recruitment agencies', roles: ['Compliance', 'Bookings', 'Payroll', 'Finance', 'Resourcing', 'Umbrella checks'] },
  { label: 'Education recruitment agencies', roles: ['Safeguarding compliance', 'Supply bookings', 'Payroll and timesheets', 'Finance', 'Resourcing'] },
  { label: 'Construction recruitment agencies', roles: ['Compliance and site cards', 'Bookings', 'Payroll and timesheets', 'Finance', 'Resourcing', 'Umbrella checks'] },
  { label: 'Care providers: home care, care homes, nursing homes', roles: ['Recruitment admin', 'Rotas and scheduling', 'Staff compliance and training', 'Payroll', 'Invoicing and finance', 'Call handling'] },
  { label: 'Dental groups and private clinics', roles: ['Appointment booking', 'Patient admin and recalls', 'Clinician compliance', 'Billing and payments', 'Call handling'] },
  { label: 'Nurseries and childcare', roles: ['Funding claims and invoicing', 'Enquiries', 'Staff DBS and qualifications', 'Rota and ratio planning', 'Payroll'] },
  { label: 'Property and block management', roles: ['Tenancy and compliance admin', 'Service charge admin', 'Arrears and credit control', 'Maintenance and contractors', 'Tenant and leaseholder queries', 'Compliance certificates'] },
  { label: 'Construction subcontractors', roles: ['Applications for payment', 'Credit control', 'CIS payroll admin', 'Timesheets', 'CSCS and site cards'] },
  { label: 'Cleaning and facilities management', roles: ['Right to work checks', 'Onboarding', 'Rotas and cover', 'Timesheets and payroll', 'Client invoicing', 'Helpdesk and job logging'] },
  { label: 'Security companies', roles: ['BS 7858 screening admin', 'SIA licence checks', 'Shift scheduling', 'Timesheets and billing', 'Payroll', 'Client reporting'] },
  { label: 'Payroll bureaus and umbrella companies', roles: ['Compliance records', 'Worker onboarding', 'Timesheet processing', 'Pay runs', 'Query handling'] },
  { label: 'Accountancy practices', roles: ['Bookkeeping', 'MTD quarterly updates', 'VAT return preparation', 'Payroll', 'Onboarding and AML admin', 'Practice admin'] }
];
/* Set per page in the document head: the team plan preset and how many FAQ items the page has */
var CCMS_PAGE = (typeof window !== 'undefined' && window.CCMS_PAGE) || {};
var CCMS_START = CCMS_PAGE.industry || 0;
function ccmsStartMix(i) { return CCMS_INDUSTRIES[i].roles.map(function (r, k) { return k === 0 ? 2 : (k < 3 ? 1 : 0); }); }

var CCMS_TASKS = ['Compliance records checked', 'Rotas and shifts updated', 'Timesheets processed', 'Invoices sent and chased', 'Calls and emails handled'];

var CCMS_SERVICES = [
  { name: 'Compliance', desc: 'Every file complete, current and audit-ready.' },
  { name: 'Bookings', desc: 'Shifts filled, staff confirmed, clients updated.' },
  { name: 'Payroll', desc: 'Every pay run right and on time.' },
  { name: 'Finance', desc: 'Invoices out, cash in, books clean.' },
  { name: 'Resourcing', desc: 'Candidates found, screened and registered.' }
];

var CCMS_GROUPS6 = [
  { num: '01', name: 'Recruitment', photo: 'Recruitment team at work', img: './assets/ed3e8c66f268d39a0f6e8cb060b92af4.jpg', tint: 'linear-gradient(160deg,#E4E9FF,#CFD7FA)', sectors: ['Healthcare recruitment agencies', 'Education recruitment agencies', 'Construction recruitment agencies'] },
  { num: '02', name: 'Care and Health', photo: 'Care admin team', img: './assets/ed0294305e66ad6d4dbececfba0bc8dd.jpg', tint: 'linear-gradient(160deg,#E3F2EA,#CBE5D7)', sectors: ['Care providers: home care, care homes, nursing homes', 'Dental groups and private clinics', 'Nurseries and childcare'] },
  { num: '03', name: 'Property, Facilities and Security', photo: 'Operations desk', img: './assets/2d0ce4a076ef8df54705d9622d174413.jpg', tint: 'linear-gradient(160deg,#ECE8FA,#D9D2F3)', sectors: ['Property and block management', 'Construction subcontractors', 'Cleaning and facilities management', 'Security companies'] },
  { num: '04', name: 'Payroll and Finance', photo: 'Finance team', img: './assets/1cb1da7470562d009acabbf10e59b8b0.jpg', tint: 'linear-gradient(160deg,#E2EFF7,#CAE1EF)', sectors: ['Payroll bureaus and umbrella companies', 'Accountancy practices'] }
];

function ccmsBookDays() {
  var out = [], d = new Date(), names = ['Sun','Mon','Tue','Wed','Thu','Fri','Sat'], mons = ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec'];
  var times = [['09:30','11:00','14:30'],['10:00','13:30','15:30'],['09:00','12:00','16:00']];
  while (out.length < 3) {
    d.setDate(d.getDate() + 1);
    var w = d.getDay(); if (w === 0 || w === 6) continue;
    var tt = times[out.length]; out.push({ label: names[w] + ' ' + d.getDate() + ' ' + mons[d.getMonth()], t1: tt[0], t2: tt[1], t3: tt[2] });
  }
  return out;
}
class Component extends DCLogic {
  constructor(props) {
    super(props);
    this.state = { open: 0, menuOpen: false, industry: CCMS_START, counts: ccmsStartMix(CCMS_START), sent: false, svc: 0, picked: false, indTab: 0, formStep: 1, planSent: false, guideSent: false, explSent: false, heroSent: false, cc: { staff: 4, sal: 28000, leave: 1, hrs: 6 }, stick: false, nearForm: false };
    this.lasers = [];
  }
  baseSettings() {
    var p = this.props;
    return {
      color: p.laserColor || '#3847ff', palette: p.auroraBeam === false ? 'classic' : 'aurora', beamPosition: 0.62, surfaceLevel: 1,
      intensity: p.intensity ?? 1.15, beamWidth: 1.5, flare: 1.5, spread: 1.5, spill: 1,
      fog: p.fog ?? 0.2, dust: 1.6, streaks: 1.5, dots: 1, pulse: 1.5,
      speed: p.speed ?? 1.5, seed: 3, mouseInteraction: true, intro: !CCMS_PAGE.clouds, clouds: !!CCMS_PAGE.clouds
    };
  }
  componentDidMount() {
    var self = this;
    this.mount(0);
    this.timer = setInterval(function () {
      if (self.state.picked || self.props.autoplayServices === false) return;
      self.setState({ svc: (self.state.svc + 1) % CCMS_SERVICES.length });
    }, 6000);
  }
  mount(tries) {
    var self = this;
    var q = function (k) { return document.querySelector('[data-ccms="' + k + '"]'); };
    var hero = q('hero'), heroCv = q('hero-canvas'), heroSurf = q('hero-surface');
    var cta = q('cta'), ctaCv = q('cta-canvas'), ctaSurf = q('cta-surface');
    if (!hero || !heroCv || !heroSurf || !cta || !ctaCv || !ctaSurf) {
      if (tries < 40) this.retry = setTimeout(function () { self.mount(tries + 1); }, 120);
      return;
    }
    function aim(box, surf, frac) {
      var b = box.getBoundingClientRect(), r = surf.getBoundingClientRect();
      return (b.width > 0 && r.width > 0) ? (r.left - b.left + r.width * frac) / b.width : 0.6;
    }
    var a = createLaserFlow(hero, heroCv, function () { return heroSurf; }, function () {
      var s = self.baseSettings();
      s.beamPosition = aim(hero, heroSurf, hero.clientWidth < 760 ? 0.9 : (self.props.beamPosition ?? 0.76));
      return s;
    });
    var b = createLaserFlow(cta, ctaCv, function () { return ctaSurf; }, function () {
      var s = self.baseSettings();
      s.beamPosition = aim(cta, ctaSurf, cta.clientWidth < 760 ? 0.82 : 0.32);
      s.seed = 7; s.spread = 1.3;
      return s;
    });
    this.lasers = [a, b].filter(Boolean);
    this.setupAnims();
    this.setupFloat();
    this.setupStick(hero, cta);
  }
  setupStick(hero, cta) {
    var self = this;
    if (!('IntersectionObserver' in window)) return;
    this.stickIO = new IntersectionObserver(function (es) {
      es.forEach(function (e) {
        if (e.target === hero) { var on = !e.isIntersecting; if (on !== self.state.stick) self.setState({ stick: on }); }
        else { var nf = e.isIntersecting; if (nf !== self.state.nearForm) self.setState({ nearForm: nf }); }
      });
    }, { threshold: 0 });
    this.stickIO.observe(hero); this.stickIO.observe(cta);
  }
  setupFloat() {
    var self = this;
    this.floatIOs = []; this.floatNodes = [];
    var se = document.scrollingElement || document.documentElement;
    if (se.scrollHeight > window.innerHeight + 40) return; /* page scrolls itself: native sticky handles it */
    if (!('IntersectionObserver' in window)) return;
    var STEP = 16, GAP = 24;
    document.querySelectorAll('.chap').forEach(function (chap) {
      var head = chap.querySelector('.chap-head');
      if (!head) return;
      head.style.position = 'relative';
      head.style.top = '0';
      head.style.transition = 'transform 180ms cubic-bezier(.23,1,.32,1)';
      head.style.willChange = 'transform';
      var layer = document.createElement('div');
      layer.setAttribute('aria-hidden', 'true');
      layer.style.cssText = 'position:absolute;left:0;width:1px;pointer-events:none;visibility:hidden';
      document.body.appendChild(layer);
      self.floatNodes.push(layer);
      var vis = {};
      function place() {
        var r = chap.getBoundingClientRect(), se2 = document.scrollingElement || document.documentElement;
        layer.style.top = (r.top + se2.scrollTop) + 'px';
        layer.style.height = r.height + 'px';
        layer.innerHTML = '';
        var n = Math.ceil(r.height / STEP);
        for (var i = 0; i < n; i++) {
          var d = document.createElement('div');
          d.style.cssText = 'position:absolute;left:0;width:1px;height:1px;top:' + (i * STEP) + 'px';
          d.dataset.i = i;
          layer.appendChild(d);
        }
        return layer.children;
      }
      function apply() {
        if (window.innerWidth < 980) { head.style.transform = 'none'; return; }
        var keys = Object.keys(vis);
        if (!keys.length) return;
        var first = Math.min.apply(null, keys.map(Number));
        var max = Math.max(0, chap.offsetHeight - head.offsetHeight);
        var y = first > 0 ? first * STEP + GAP : 0;
        head.style.transform = 'translateY(' + Math.min(max, y) + 'px)';
      }
      var io = new IntersectionObserver(function (entries) {
        entries.forEach(function (e) {
          var i = e.target.dataset.i;
          if (e.isIntersecting) vis[i] = 1; else delete vis[i];
        });
        apply();
      });
      Array.prototype.forEach.call(place(), function (d) { io.observe(d); });
      self.floatIOs.push(io);
      var ro = new ResizeObserver(function () {
        io.disconnect(); vis = {};
        Array.prototype.forEach.call(place(), function (d) { io.observe(d); });
      });
      ro.observe(chap);
      self.floatIOs.push(ro);
    });
  }
  setupAnims() {
    if (window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches) return;
    if (!('IntersectionObserver' in window)) return;
    var KF = {
      up: [{ opacity: 0, transform: 'translateY(18px)' }, { opacity: 1, transform: 'none' }],
      fade: [{ opacity: 0 }, { opacity: 1 }],
      pop: [{ opacity: 0, transform: 'scale(.6)' }, { opacity: 1, transform: 'scale(1)' }],
      barx: [{ transform: 'scaleX(0)' }, { transform: 'scaleX(1)' }],
      bary: [{ transform: 'scaleY(.1)' }, { transform: 'scaleY(1)' }],
      draw: [{ strokeDashoffset: 700 }, { strokeDashoffset: 0 }]
    };
    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (en) {
        if (!en.isIntersecting) return;
        var el = en.target; io.unobserve(el);
        var k = el.getAttribute('data-a'), d = +el.getAttribute('data-d') || 0;
        if (!KF[k] || !el.animate) return;
        /* Section reveals stay under a third of a second and show cards together; mock-up animations keep their timing */
        var quick = k === 'up' || k === 'fade';
        try { el.animate(KF[k], { duration: quick ? 300 : (k === 'draw' ? 1400 : (k === 'barx' ? 1100 : 700)), delay: quick ? 0 : d, easing: 'cubic-bezier(.23,1,.32,1)', fill: 'backwards' }); } catch (e) {}
      });
    }, { threshold: 0.01 });
    document.querySelectorAll('[data-a]').forEach(function (el) { io.observe(el); });
    this.io = io;
  }
  componentDidUpdate() { this.lasers.forEach(function (l) { l.wake(); }); }
  componentWillUnmount() {
    clearTimeout(this.retry); clearInterval(this.timer); if (this.io) this.io.disconnect(); if (this.stickIO) this.stickIO.disconnect(); (this.floatIOs || []).forEach(function (x) { x.disconnect(); }); (this.floatNodes || []).forEach(function (n) { n.remove(); });
    this.lasers.forEach(function (l) { l.destroy(); });
    this.lasers = [];
  }
  leadOk(e, key) {
    if (e && e.preventDefault) e.preventDefault();
    var t = e && (e.currentTarget || e.target);
    var f = t && t.closest ? t.closest('form') : null;
    var ins = f ? f.querySelectorAll('input') : [];
    for (var i = 0; i < ins.length; i++) { if (!ins[i].checkValidity()) { ins[i].reportValidity(); return; } }
    var o = {}; o[key] = true; this.setState(o);
  }
  goStep2(e) {
    var t = e && (e.currentTarget || e.target);
    var f = t && t.closest ? t.closest('form') : document.querySelector('[data-ccms="cta-surface"]');
    var box = f ? f.querySelector('[data-step1]') : null;
    if (box) {
      var ins = box.querySelectorAll('input');
      for (var i = 0; i < ins.length; i++) { if (!ins[i].checkValidity()) { ins[i].reportValidity(); return; } }
    }
    this.setState({ formStep: 2 });
  }
  renderVals() {
    var self = this;
    var ind = this.state.industry, counts = this.state.counts, roles = CCMS_INDUSTRIES[ind].roles;
    var total = counts.reduce(function (a, b) { return a + b; }, 0);
    var svc = this.state.svc;
    var auto = !this.state.picked && this.props.autoplayServices !== false;
    var cc = this.state.cc;
    var gbp = function (n) { return '£' + Math.round(n).toLocaleString('en-GB'); };
    var pct = function (v, a, b) { return ((v - a) / (b - a) * 100).toFixed(1) + '%'; };
    var setCC = function (k) { return function (e) { var v = parseInt(e && e.target ? e.target.value : 0, 10) || 0; var o = Object.assign({}, self.state.cc); o[k] = v; self.setState({ cc: o }); }; };
    /* UK assumptions: employer NI 15% above £5,000, 3% pension, replacing a leaver costs 20% of salary, manager time at £30 an hour over 46 working weeks */
    var ccPeople = cc.staff * (cc.sal + Math.max(0, cc.sal - 5000) * 0.15 + cc.sal * 0.03);
    var ccTurn = cc.leave * cc.sal * 0.2;
    var ccMgr = cc.hrs * 46 * 30;
    var vals = {
      menuOpen: this.state.menuOpen,
      menuExpanded: this.state.menuOpen ? 'true' : 'false',
      toggleMenu: function () { self.setState({ menuOpen: !self.state.menuOpen }); },
      closeMenu: function () { self.setState({ menuOpen: false }); },
      logos: Array.from({ length: 16 }, function (_, i) { return { hidden: i >= 8 ? 'true' : 'false', shape: ['50%', '6px', '50% 50% 6px 6px', '6px 50% 6px 50%'][i % 4] }; }),
      hires: Array.from({ length: 20 }, function (_, i) {
        var hired = i === 13;
        return { bg: hired ? '#2F4BFF' : '#C9CFE6', ring: hired ? '0 0 0 4px rgba(47,75,255,.22)' : 'none', d: (i * 1.2).toFixed(1) + '%' };
      }),
      tasks: CCMS_TASKS.map(function (t, i) { return { label: t, d: (i * 4) + '%', d2: (i * 4 + 6) + '%' }; }),
      svcName: CCMS_SERVICES[svc].name,
      svc0: svc === 0, svc1: svc === 1, svc2: svc === 2, svc3: svc === 3, svc4: svc === 4,
      services: CCMS_SERVICES.map(function (s, i) {
        var active = svc === i;
        return {
          name: s.name, desc: s.desc, active: active, num: '0' + (i + 1), numColor: active ? '#2238D6' : '#9297A2',
          pressed: active ? 'true' : 'false',
          color: active ? '#0B0C0F' : '#626875',
          arrowOp: active ? '1' : '0',
          barWidth: auto ? '0%' : '100%',
          barAnim: auto ? 'ccms-width 6s linear both' : 'none',
          pick: function () { self.setState({ svc: i, picked: true }); }
        };
      }),
      indTabs: CCMS_GROUPS6.map(function (g, i) {
        var on = self.state.indTab === i;
        return { name: g.name, num: g.num, pressed: on ? 'true' : 'false', color: on ? '#0B0D12' : '#8A909C', numColor: on ? '#2238D6' : '#B4B9C4', pick: function () { self.setState({ indTab: i }); } };
      }),
      indName: CCMS_GROUPS6[this.state.indTab].name,
      indNum: CCMS_GROUPS6[this.state.indTab].num,
      indPhoto: CCMS_GROUPS6[this.state.indTab].photo,
      indAlt: CCMS_GROUPS6[this.state.indTab].photo,
      indImg: CCMS_GROUPS6[this.state.indTab].img,
      indTint: CCMS_GROUPS6[this.state.indTab].tint,
      indSectors: CCMS_GROUPS6[this.state.indTab].sectors,
      industryValue: String(ind),
      industryOptions: CCMS_INDUSTRIES.map(function (o, i) { return { value: String(i), label: o.label }; }),
      pickIndustry: function (e) {
        var n = parseInt(e && e.target ? e.target.value : 0, 10) || 0;
        self.setState({ industry: n, counts: ccmsStartMix(n) });
      },
      roles: roles.map(function (r, k) {
        return {
          name: r, count: counts[k],
          decLabel: 'Remove one ' + r + ' role', incLabel: 'Add one ' + r + ' role',
          dec: function () { var c = self.state.counts.slice(); c[k] = Math.max(0, c[k] - 1); self.setState({ counts: c }); },
          inc: function () { var c = self.state.counts.slice(); c[k] = Math.min(50, c[k] + 1); self.setState({ counts: c }); }
        };
      }),
      total: total,
      totalLabel: total === 1 ? 'person' : 'people',
      industryLabel: CCMS_INDUSTRIES[ind].label,
      chosen: roles.map(function (r, k) { return { name: r, count: counts[k] }; }).filter(function (c) { return c.count > 0; }),
      noneChosen: total === 0,
      sent: this.state.sent,
      notSent: !this.state.sent,
      formBody: this.state.sent ? 'none' : 'block',
      s1: this.state.formStep === 1 ? 'block' : 'none',
      s2: this.state.formStep === 2 ? 'block' : 'none',
      stepNum: this.state.sent ? 2 : this.state.formStep,
      stepPct: this.state.sent ? '100%' : (this.state.formStep === 1 ? '50%' : '100%'),
      stepName: this.state.sent ? 'Done' : (this.state.formStep === 1 ? 'Your details' : 'Your team'),
      nextStep: function (e) { self.goStep2(e); },
      prevStep: function () { self.setState({ formStep: 1 }); },
      bookDays: ccmsBookDays(),
      finishForm: function () { self.setState({ sent: true }); },
      planSent: this.state.planSent, planNotSent: !this.state.planSent,
      sendPlan: function (e) { self.leadOk(e, 'planSent'); },
      guideSent: this.state.guideSent, guideNotSent: !this.state.guideSent,
      sendGuide: function (e) { self.leadOk(e, 'guideSent'); },
      heroSent: this.state.heroSent, heroNotSent: !this.state.heroSent,
      ccStaff: cc.staff, ccSal: cc.sal, ccLeave: cc.leave, ccHrs: cc.hrs,
      ccStaffPct: pct(cc.staff, 1, 30), ccSalPct: pct(cc.sal, 20000, 50000), ccLeavePct: pct(cc.leave, 0, 10), ccHrsPct: pct(cc.hrs, 0, 20),
      ccStaffTxt: cc.staff + (cc.staff === 1 ? ' person' : ' people'), ccSalTxt: gbp(cc.sal), ccLeaveTxt: String(cc.leave), ccHrsTxt: cc.hrs + ' hrs',
      ccInhouse: gbp(total * (cc.sal + Math.max(0, cc.sal - 5000) * 0.15 + cc.sal * 0.03)), ccPeople: gbp(ccPeople), ccTurn: gbp(ccTurn), ccMgr: gbp(ccMgr), ccMgrHrs: (cc.hrs * 46).toLocaleString('en-GB'), ccTotal: gbp(ccPeople + ccTurn + ccMgr),
      setStaff: setCC('staff'), setSal: setCC('sal'), setLeave: setCC('leave'), setHrs: setCC('hrs'),
      heroSend: function (e) { self.leadOk(e, 'heroSent'); },
      explSent: this.state.explSent, explNotSent: !this.state.explSent,
      sendExpl: function (e) { self.leadOk(e, 'explSent'); },
      stickCls: this.state.stick && !this.state.nearForm ? 'stick on' : 'stick',
      mbarCls: this.state.stick && !this.state.nearForm ? 'mbar on' : 'mbar',
      submitForm: function (e) { if (e && e.preventDefault) e.preventDefault(); if (self.state.formStep === 1) { self.goStep2(e); return; } self.setState({ sent: true }); },
      faqs: []
    };
    /* FAQ answers are written into the page; these flat keys drive each item's open state */
    for (var fi = 0; fi < (CCMS_PAGE.faqCount || 0); fi++) {
      (function (i) {
        var open = self.state.open === i;
        vals['fq' + i + 'e'] = open ? 'true' : 'false';
        vals['fq' + i + 'd'] = open ? 'block' : 'none';
        vals['fq' + i + 'b'] = open ? '#2F4BFF' : '#FFFFFF';
        vals['fq' + i + 'c'] = open ? '#FFFFFF' : '#0B0C0F';
        vals['fq' + i + 'r'] = open ? 'rotate(45deg)' : 'none';
        vals['fq' + i + 't'] = function () { self.setState({ open: open ? -1 : i }); };
      })(fi);
    }
    return vals;
  }
}
