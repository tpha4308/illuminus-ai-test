
Files directory:
- `contour-normalisation.md`: Report for question 1
- `ai-video-generation.md`: Proposal for question 2

Dataset:
- Human Segmentation dataset: taken from https://github.com/VikramShenoy97/Human-Segmentation-Dataset/tree/master 
- modis-dataset: taken from https://www.kaggle.com/datasets/abdallahelsayed22/modis-dataset

An example of running contour normalisation:
```bash
python main.py --img_path square.jpg --N 10 --decrease_method angle
```
where
- `img_path`: relative path to the binary mask image
- `N`: desired contour length
- Decrease method: methods in decreasing contour length, available methods inclue `angle`, `straight`, and `area`.