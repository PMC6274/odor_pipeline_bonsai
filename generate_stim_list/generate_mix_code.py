from pathlib import Path

# A B C D E F 开启时对应输出值
odor_values = [1, 2, 3, 5, 6, 7]

def make_line(it: int) -> str:
    outputs = []
    on_count = 0

    for bit, val in enumerate(odor_values):
        if it & (1 << bit):
            outputs.append(val)
            on_count += 1
        else:
            outputs.append(0)

    flow = 900 - 100 * on_count
    payload = ",".join(map(str, outputs + [flow]))

    if it < 10:
        return f'it == {it}  ? "{payload}" :'
    else:
        return f'it == {it} ? "{payload}" :'

def generate_bonsai_condition_txt(output_file="bonsai_conditions.txt"):
    lines = [make_line(i) for i in range(1, 64)]
    lines.append('"0,0,0,0,0,0,0"')
    Path(output_file).write_text("\n".join(lines), encoding="utf-8")
    print(f"Saved to {output_file}")

if __name__ == "__main__":
    generate_bonsai_condition_txt()