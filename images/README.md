# Device Images

This folder should contain images of the four device types:

- **Turbine.jpg** or **Turbine.png** - Wind turbine images
- **ThermalEngine.jpg** or **ThermalEngine.png** - Thermal engine images
- **ElectricalRotor.jpg** or **ElectricalRotor.png** - Electrical rotor images
- **OilAndGas.jpg** or **OilAndGas.png** - Oil and gas equipment images

## Usage

These images are used by the Cohere AI image analysis feature. To use:

1. Place your device images in this folder
2. Use the API endpoint: `POST /api/monitoring/ai/analyze-image`
3. Pass the image name as a query parameter: `?image_name=Turbine.jpg`

## Supported Formats

- JPEG (.jpg, .jpeg)
- PNG (.png)
- GIF (.gif)

## Example API Call

```bash
curl -X POST "http://localhost:8000/api/monitoring/ai/analyze-image?image_name=Turbine.jpg&query=Analyze this device" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

## Note

If you don't have device images, the system will still work. The AI features will use text-based analysis only.
