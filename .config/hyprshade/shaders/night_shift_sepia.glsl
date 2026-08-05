#version 300 es
precision highp float; // Cambiado a highp para evitar fluctuaciones de precisión en coma flotante

in vec2 v_texcoord;
out vec4 fragColor;

uniform sampler2D tex;

// --- Parámetros estables ---
const float DESATURACION = 0.65;
const float REDUCCION_GAMMA = 0.85;
const vec3 TONO_SEPIA = vec3(0.95, 0.78, 0.55);

void main() {
    // Obtenemos el color asegurando la precisión de coordenadas
    vec4 colorOriginal = texture(tex, vec2(v_texcoord.x, v_texcoord.y));
    vec3 rgb = colorOriginal.rgb;

    // Fórmula estándar de luminancia ultra-compatible
    float luminancia = dot(rgb, vec3(0.2126, 0.7152, 0.0722));

    // Desaturar
    vec3 colorDesaturado = mix(rgb, vec3(luminancia), DESATURACION);

    // Aplicar Sepia
    vec3 colorSepia = colorDesaturado * TONO_SEPIA;

    // Corrección de gamma estable (evita divisiones complejas en tiempo de ejecución)
    // 1.0 / 0.85 es aprox 1.176
    vec3 colorFinal = pow(colorSepia, vec3(1.176));

    fragColor = vec4(colorFinal, colorOriginal.a);
}
