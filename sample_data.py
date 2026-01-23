import csv
import os
import random


def read_rows(path):
    with open(path, "r", encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        rows = list(reader)
        return reader.fieldnames, rows


def write_rows(path, fieldnames, rows):
    with open(path, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def sample_rows(rows, n):
    if len(rows) <= n:
        return rows
    return random.sample(rows, n)


def main():
    data_dir = os.path.join(os.path.dirname(__file__), "data")
    negative_path = os.path.join(data_dir, "negativve_data.csv")
    positive_path = os.path.join(data_dir, "positive_data.csv")
    output_path = os.path.join(data_dir, "sampled_data_1.csv")

    random.seed(43)
    # random.seed(42)

    neg_fields, neg_rows = read_rows(negative_path)
    pos_fields, pos_rows = read_rows(positive_path)

    if neg_fields != pos_fields:
        raise ValueError("negative_data 和 positive_data 的列名不一致")

    sampled_neg = sample_rows(neg_rows, 500)
    sampled_pos = sample_rows(pos_rows, 500)

    combined = sampled_neg + sampled_pos
    random.shuffle(combined)

    write_rows(output_path, neg_fields, combined)
    print(f"已写入: {output_path}")


if __name__ == "__main__":
    main()
