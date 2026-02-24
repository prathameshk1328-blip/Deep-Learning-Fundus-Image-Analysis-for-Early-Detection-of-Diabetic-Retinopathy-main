# =========================================
# COMPLETE XCEPTION PIPELINE (KAGGLEHUB)
# =========================================

# !pip install -q kagglehub split-folders seaborn scikit-learn

import kagglehub
import os, shutil, glob
import splitfolders
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import tensorflow as tf

# -------------------------------------------------
# 1. Download dataset using kagglehub
# -------------------------------------------------

dataset_path = kagglehub.dataset_download("arbethi/diabetic-retinopathy-level-detection")
print("Dataset path:", dataset_path)

# Clean old folders
for f in ["data"]:
    if os.path.exists(f):
        shutil.rmtree(f)

# -------------------------------------------------
# 2. Auto-detect image folder
# -------------------------------------------------

folders = glob.glob(dataset_path + "/**/", recursive=True)

img_folder = None
for f in folders:
    if len(glob.glob(f + "*/*.png")) > 10 or len(glob.glob(f + "*/*.jpg")) > 10:
        img_folder = f
        break

if img_folder is None:
    raise RuntimeError("Could not automatically find image folder.")

print("Detected image folder:", img_folder)

# -------------------------------------------------
# 3. Split train / validation
# -------------------------------------------------

splitfolders.ratio(
    img_folder,
    output="data",
    seed=42,
    ratio=(0.8, 0.2)
)

# -------------------------------------------------
# 4. Parameters
# -------------------------------------------------

IMG = 229
BATCH = 32
EPOCHS = 30

from tensorflow.keras.preprocessing.image import ImageDataGenerator

train_gen = ImageDataGenerator(
    rescale=1./255,
    rotation_range=25,
    zoom_range=0.2,
    width_shift_range=0.1,
    height_shift_range=0.1,
    horizontal_flip=True
)

val_gen = ImageDataGenerator(rescale=1./255)

train_data = train_gen.flow_from_directory(
    "data/train",
    target_size=(IMG, IMG),
    batch_size=BATCH,
    class_mode="categorical"
)

val_data = val_gen.flow_from_directory(
    "data/val",
    target_size=(IMG, IMG),
    batch_size=BATCH,
    class_mode="categorical",
    shuffle=False
)

NUM_CLASSES = train_data.num_classes
print("Classes:", train_data.class_indices)

# -------------------------------------------------
# 5. Xception Model
# -------------------------------------------------

from tensorflow.keras.applications import Xception
from tensorflow.keras.layers import Dense, Flatten
from tensorflow.keras.models import Model

base = Xception(
    input_shape=(IMG, IMG, 3),
    weights="imagenet",
    include_top=False
)

for l in base.layers:
    l.trainable = False

x = Flatten()(base.output)
out = Dense(NUM_CLASSES, activation="softmax")(x)

model = Model(base.input, out)

model.compile(
    optimizer="adam",
    loss="categorical_crossentropy",
    metrics=["accuracy"]
)

model.summary()

# -------------------------------------------------
# 6. Train
# -------------------------------------------------

from tensorflow.keras.callbacks import ModelCheckpoint

ckpt = ModelCheckpoint(
    "best_model.h5",
    monitor="val_loss",
    save_best_only=True
)

history = model.fit(
    train_data,
    epochs=EPOCHS,
    validation_data=val_data,
    steps_per_epoch=train_data.samples // BATCH,
    validation_steps=val_data.samples // BATCH,
    callbacks=[ckpt]
)

model.save("final_xception_diabetic_retinopathy.h5")

# -------------------------------------------------
# 7. Accuracy / Loss plots
# -------------------------------------------------

plt.figure()
plt.plot(history.history["accuracy"])
plt.plot(history.history["val_accuracy"])
plt.legend(["train", "val"])
plt.title("Accuracy")
plt.savefig("accuracy.png")
plt.show()

plt.figure()
plt.plot(history.history["loss"])
plt.plot(history.history["val_loss"])
plt.legend(["train", "val"])
plt.title("Loss")
plt.savefig("loss.png")
plt.show()

# -------------------------------------------------
# 8. Confusion Matrix + ROC
# -------------------------------------------------

from sklearn.metrics import confusion_matrix, roc_curve, auc
from sklearn.preprocessing import label_binarize

pred = model.predict(val_data)
y_pred = np.argmax(pred, axis=1)
y_true = val_data.classes

cm = confusion_matrix(y_true, y_pred)

plt.figure(figsize=(6,5))
sns.heatmap(cm, annot=True, fmt="d", cmap="Blues")
plt.title("Confusion Matrix")
plt.savefig("confusion_matrix.png")
plt.show()

y_bin = label_binarize(y_true, classes=list(range(NUM_CLASSES)))

plt.figure()
for i in range(NUM_CLASSES):
    fpr, tpr, _ = roc_curve(y_bin[:, i], pred[:, i])
    plt.plot(fpr, tpr, label=f"class {i} AUC={auc(fpr,tpr):.2f}")

plt.legend()
plt.title("ROC Curves")
plt.savefig("roc.png")
plt.show()

# -------------------------------------------------
# 9. Final outputs
# -------------------------------------------------

print("\nSUCCESS")
print("Saved:")
print("best_model.h5")
print("final_xception_diabetic_retinopathy.h5")
print("accuracy.png")
print("loss.png")
print("confusion_matrix.png")
print("roc.png")
