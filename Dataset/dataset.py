import os, csv, cv2

def arrange(path, max, save_count = 1, read_count = 1):
    while (read_count <= max):
        img = "{}\\{}.jpg".format(path, read_count)
        if (not os.path.exists(img)):
            read_count += 1
            continue

        print("[%d] %s" % (save_count, img), end = "\t")
        while (True):
            try:
                row = next(origin_data)
                row0 = int(row[0])
                row2 = float(row[2])
            except BaseException as err:
                print(type(err), err)
                return

            if (row0 == read_count):
                print(row, end = "\t")

                if (row2 < 0):
                    print("removed")
                    try:
                        os.remove(img)
                    except BaseException as err:
                        print(type(err), err)
                        return
                    break

                try:
                    row[0] = save_count
                    image = cv2.imread(img) # Corrupt JPEG data: premature end of data segment
                    cv2.imwrite("{}\\output\\{}.jpg".format(path, save_count), image)
                    output_data.writerow(row)
                except BaseException as err:
                    print("faild\n", type(err), err)
                    return
                save_count += 1
                read_count += 1
                print("save")
                break

while (True):
    path = input("dataset path: ")
    if (not os.path.exists(path)):
        print("%s dose not exist, try again" % path)
        continue

    try:
        origin = open(path + "\\dataset.csv", "r")
        if not os.path.exists(path + "\\output"):
            os.makedirs(path + "\\output")
        output = open(path + "\\output\\output.csv", "w")
        origin_data = csv.reader(origin)
        output_data = csv.writer(output, lineterminator = "\n")
        read = int(input("read start numer: "))
        save = int(input("save start numer: "))
        max = int(input("max numer: "))
    except BaseException as err:
        print(type(err), err, ", try again")
        continue
    break
arrange(path, max, save, read)
origin.close()
output.close()

