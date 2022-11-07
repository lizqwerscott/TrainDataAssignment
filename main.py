import os
import json
import shutil
import utils
import random

def load_data(path: str) -> list:
    result = []

    for root, dirs, files in os.walk(path):
        for name in files:
            file_name, file_extension = os.path.splitext(name)

            find_p = None
            for item in result:
                if item["name"] == file_name:
                    find_p = item
                    break

            if find_p != None:
                if file_extension in [".jpg", ".png"]:
                    find_p["image"] = os.path.join(root, name)
                elif file_extension == ".txt":
                    find_p["label"] = os.path.join(root, name)
                else:
                    print("error: {}".format(os.path.join(root, name)))
            else:
                data = {}
                data["name"] = file_name
                if file_extension in [".jpg", ".png"]:
                    data["image"] = os.path.join(root, name)
                elif file_extension == ".txt":
                    data["label"] = os.path.join(root, name)

                if len(data.keys()) == 2:
                    result.append(data)

    return result

def split_train_var(data: list, scale: list):
    length = len(data)
    val_len = int(length * scale[1] * 0.1)
    test_len = int(length * scale[2] * 0.1)
    if val_len == 0:
        val_len = 1
    if test_len == 0:
        test_len = 1

    if scale[1] == 0:
        val_len = 0

    test_list = data[0:test_len]
    val_list = data[test_len:test_len + val_len]
    train_list = data[test_len + val_len:-1]

    return (train_list, val_list, test_list)

def move_train_data(output_path: str, data: list):
    images_path = "{}{}/".format(output_path, "images")
    labels_path = "{}{}/".format(output_path, "labels")

    utils.make_dir(images_path)
    utils.make_dir(labels_path)

    for file in data:
        picture_name = os.path.basename(file["image"])
        label_name = os.path.basename(file["label"])

        shutil.copy(file["image"], "{}{}".format(images_path, picture_name))
        shutil.copy(file["image"], "{}{}".format(labels_path, label_name))

def handle_data(data: list, result_path: str, split_scale = [7, 1, 2]):

    random.shuffle(data)

    train_list, val_list, test_list = split_train_var(data, split_scale)

    train_path = "{}{}/".format(result_path, "train")
    val_path = "{}{}/".format(result_path, "val")
    test_path = "{}{}/".format(result_path, "test")

    move_train_data(train_path, train_list)
    move_train_data(val_path, val_list)
    move_train_data(test_path, test_list)

if __name__ == "__main__":
    data_path = "./data/"
    result_path = "./output/"

    utils.make_dir(data_path)
    utils.make_dir(result_path)

    datas = load_data(data_path)

    handle_data(datas, result_path)
