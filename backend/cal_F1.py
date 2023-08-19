import os
from glob import glob
from sklearn.metrics import precision_recall_fscore_support
import numpy as np
import requests
from PIL import Image

def load_images_from_folder(folder_path):
    images = []
    labels = []
    for class_folder in os.listdir(folder_path):
        class_path = os.path.join(folder_path, class_folder)
        if os.path.isdir(class_path):
            for img_file in glob(os.path.join(class_path, '*.*')):
                with open(img_file, 'rb') as f:
                    img = f.read()
                    images.append(img)
                    labels.append(class_folder)
    return images, labels

def get_predictions(images):
    predictions = []
    for img in images:
        # Use the given server to make predictions
        response = requests.post("http://127.0.0.1:5007/azure_cog/", files={"image": img})
        pred_scores = response.json()
        pred_label = class_names[np.argmax(list(pred_scores.values())[0])]
        predictions.append(pred_label)
    return predictions

def evaluate_model(folder_path):
    images, true_labels = load_images_from_folder(folder_path)
    pred_labels = get_predictions(images)

    precision, recall, f1_score, _ = precision_recall_fscore_support(true_labels, pred_labels, average='macro')

    print("Precision: {:.4f}, Recall: {:.4f}, F1 Score: {:.4f}".format(precision, recall, f1_score))

folder_path = "path/to/your/local/folder"
evaluate_model(folder_path)
