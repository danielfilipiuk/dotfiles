if hl.plugin.hyprglass then
    local hg = hl.plugin.hyprglass
    
--enabled	bool	true (1 in .conf)	Enable/disable the effect globally. Per-window tags override this.
--manage_window_blur	bool	true (1 in .conf)	Automatically set the noblur property on glassed windows. Glass replaces Hyprland's blur; without noblur, Hyprland's cached-blur optimization (blur:new_optimizations) hides the glass on static windows. Set to 0 to manage windowrule = noblur yourself.
--default_theme	string	dark	Default theme: dark or light
--default_preset	string	default	Default preset name
--blur_strength	float	2.0	—	—	Blur radius scale (value * 12.0 px)
--blur_iterations	int	3	—	—	Gaussian blur passes (1-5)
--refraction_strength	float	0.6	—	—	Edge refraction intensity (0.0-1.0)
--chromatic_aberration	float	0.5	—	—	Spectral dispersion at edges (0.0-1.0)
--fresnel_strength	float	0.6	—	—	Edge glow intensity (0.0-1.0)
--specular_strength	float	0.8	—	—	Specular highlight brightness (0.0-1.0)
--glass_opacity	float	1.0	—	—	Overall glass opacity (0.0-1.0)
--edge_thickness	float	0.06	—	—	Bezel width, fraction of smallest dimension (0.0-0.15)
--tint_color	color	0x8899aa22	—	—	Glass tint RRGGBBAA hex. Alpha = tint strength
--lens_distortion	float	0.5	—	—	Center dome magnification (0.0-1.0)
--brightness	float	—	0.82	1.12	Brightness multiplier
--contrast	float	—	0.90	0.92	Contrast around midpoint
--saturation	float	—	0.80	0.85	Desaturation (0 = grayscale, 1 = full)
--vibrancy	float	—	0.15	0.12	Selective saturation boost
--vibrancy_darkness	float	—	0.0	0.0	Vibrancy influence on dark areas (0-1)
--adaptive_dim	float	—	0.4	0.0	Dims bright areas behind the glass (white is white 0 -to- 1 --white becomes black)
--adaptive_boost	float	—	0.0	0.4	Boosts dark areas behind the glass (black is black 0 -to- 1 black becomes white)

    hg.config({
    	enabled = enabled,
    	--manage_window_blur = true,
        default_theme = "light", -- light - dark
        default_preset = "clear",
        tint_color = 0x000000aa,
        brightness = 0.9,
        dark = { brightness = 0.82 },
        light = { adaptive_boost = 0.5 },

	

        layers = { enabled = true },
    })

--Field	Type	Description
--preset	string	Preset override for this layer
--mask_threshold	float	Alpha threshold (pixels below this are not glassed). Default 0.001
--exclude	bool	Blacklist this namespace instead of whitelisting it

    -- Layer surfaces: each call whitelists the namespace and configures it
    hg.layer("waybar", { preset = "subtle", mask_threshold = 0.05 })
    --hg.layer("swaync")
    --hg.layer("quickshell:bezel", { preset = "ui", mask_threshold = 0.3 })
    --hg.layer("debug-panel", { exclude = true })

    -- Presets
       
 --high_contrast	Punchy colors, strong tinting, good contrast between dark and light themes. Lower blur, stronger refraction.
--subtle	Minimal glass effect. Light blur, reduced refraction and highlights.
--clear	Minimal transparent effect. Like a transparent rounded border glass plate.
--glass	Solid glass block effect with a lot of chromatic aberration.

    hg.preset("clear", {
    	 inherits = "subtle",
        glass_opacity = 0.8,
        blur_strength = 1.5,
        dark = { brightness = 0.7 },
        light = { brightness = 1.2 },
        
        
    })

    hg.preset("contrasted", {
        inherits = "high_contrast",
        contrast = 1.2,
        adaptive_dim = 1.5,
        dark = { tint_color = 0x02142aa9 },
    })
    
    hg.preset("all", {
    	blur_strength = 2.0,
        blur_iterations = 3,
        refraction_strength = 0.1,
        chromatic_aberration = 0.1,
        fresnel_strength = 0.1,
        specular_strength = 0.8,
        glass_opacity = 0.1,
        edge_thickness = 0.06,
        tint_color = 0x000000,
        lens_distortion = 0.5,
        brightness = 1.12,
        contrast = 0.52,
        saturation = 0.85,
        vibrancy = 1.12,
        vibrancy_darkness = 1.0,
        adaptive_dim = 0.0,
        adaptive_boost = 0.4,
        })
end
