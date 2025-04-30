#include "nnom.h"
#include "weights.h"
#include <algorithm>
#include <cstddef>
#include <cstdint>
#include <cstdio>
#include <fstream>
#include <ios>
#include <iostream>
#include <map>
#include <sstream>
#include <string>
#include <sys/types.h>
#include <vector>

#define QUANTIFICATION_SCALE (pow(2, INPUT_1_OUTPUT_DEC))

#ifdef NNOM_USING_STATIC_MEMORY
static uint8_t static_buf[1024 * 8];
#endif // NNOM_USING_STATIC_MEMORY

const size_t kLabelBatchSize = 128;
const size_t kSampleSize = 150;

struct validation_data_t {
  std::vector<int8_t> labels;
  std::vector<std::vector<int8_t>> samples;
};

std::map<int8_t, const char *> idx2label{
    {0, "swing-leftward"}, {1, "swing-rightward"}, {2, "swing-upward"}};

uint8_t init_nnom() {
  nnom_set_static_buf(static_buf, sizeof(static_buf));
  return 0;
}

uint8_t load_validation_bin(const char *bin_path, validation_data_t *valid_data,
                            size_t sample_size) {
  std::ifstream file(bin_path, std::ios::ate | std::ios::binary);
  if (!file.is_open()) {
    return -1;
  }
  std::streamsize size = file.tellg();
  file.seekg(0, std::ios::beg);

  size_t total_samples = 0;
  size_t pos = 0;
  while (pos < size) {
    // 读取默认填充的 128 个标签
    std::vector<int8_t> labels(kLabelBatchSize);
    file.read(reinterpret_cast<char *>(labels.data()), kLabelBatchSize);
    pos += kLabelBatchSize;

    // 判断实际的样本数量
    size_t acutal_samples = kLabelBatchSize;
    if (pos + kLabelBatchSize * sample_size > size) {
      acutal_samples = (size - pos) / sample_size;
    }

    std::vector<int8_t> data_block(acutal_samples * sample_size);
    file.read(reinterpret_cast<char *>(data_block.data()), data_block.size());
    pos += data_block.size();

    // 处理标签，去除多余的填充
    for (int i = 0; i < acutal_samples; ++i) {
      valid_data->labels.push_back(labels[i]);
    }
    // 处理数据
    for (int i = 0; i < acutal_samples; ++i) {
      auto start = data_block.begin() + i * sample_size;
      auto end = start + sample_size;
      valid_data->samples.emplace_back(start, end);
    }

    total_samples = acutal_samples;
  }
  printf("read %ld samples\n", total_samples);

  return 0;
}

uint8_t load_imu_dataset(const char *path, int8_t *data, size_t length) {
  std::ifstream file(path);
  if (!file.is_open()) {
    return -1;
  }
  std::string line;
  size_t actual_lines = 0;
  while (std::getline(file, line)) {
    std::replace(line.begin(), line.end(), ',', ' ');
    std::istringstream iss(line);
    float acc_x, acc_y, acc_z, pitch, roll, yaw;
    // printf("%5f %5f %5f %5f %5f %5f\n", acc_x * QUANTIFICATION_SCALE,
    //        acc_y * QUANTIFICATION_SCALE, acc_z * QUANTIFICATION_SCALE, pitch,
    //        roll * QUANTIFICATION_SCALE, yaw * QUANTIFICATION_SCALE);
    if (iss >> acc_x >> acc_y >> acc_z >> pitch >> roll >> yaw) {
      *(data + actual_lines * 6 + 0) = int8_t(acc_x * QUANTIFICATION_SCALE);
      *(data + actual_lines * 6 + 1) = int8_t(acc_y * QUANTIFICATION_SCALE);
      *(data + actual_lines * 6 + 2) = int8_t(acc_z * QUANTIFICATION_SCALE);
      *(data + actual_lines * 6 + 3) = int8_t(pitch * QUANTIFICATION_SCALE);
      *(data + actual_lines * 6 + 4) = int8_t(roll * QUANTIFICATION_SCALE);
      *(data + actual_lines * 6 + 5) = int8_t(yaw * QUANTIFICATION_SCALE);
      actual_lines++;
    } else {
      if (actual_lines == 0)
        continue;
      return -1;
    }
  }

  return 0;
}

uint8_t parse_val_data_imu(validation_data_t *val_data) {
  printf("[num] %5s %5s %5s %5s %5s %5s\n", "acc_x", "acc_y", "acc_z", "pitch",
         "roll", "yaw");
  for (int i = 0; i < kSampleSize; ++i) {
    printf("[%3d] %5d %5d %5d %5d %5d %5d\n", i + 1,
           val_data->samples[0][i + 0], val_data->samples[0][i + 1],
           val_data->samples[0][i + 2], val_data->samples[0][i + 3],
           val_data->samples[0][i + 4], val_data->samples[0][i + 5]);
  }
  return 0;
}

uint8_t feed_model_input(int8_t *data, size_t length) {
  for (int i = 0; i < kSampleSize; ++i) {
    nnom_input_data[i * 3 + 0] = data[i * 3 + 0];
    nnom_input_data[i * 3 + 1] = data[i * 3 + 1];
    nnom_input_data[i * 3 + 2] = data[i * 3 + 2];
    nnom_input_data[i * 3 + 3] = data[i * 3 + 3];
    nnom_input_data[i * 3 + 4] = data[i * 3 + 4];
    nnom_input_data[i * 3 + 5] = data[i * 3 + 5];
  }
  return 0;
}

inline float int8_to_prob(int8_t num) { return (num / 127.0) * 100; }

uint8_t fetch_model_output_and_print() {
  printf("label %12s %12s %12s\n", idx2label[0], idx2label[1], idx2label[2]);
  printf("conf  %12f %12f %12f\n", int8_to_prob(nnom_output_data[0]),
         int8_to_prob(nnom_output_data[1]), int8_to_prob(nnom_output_data[2]));
  return 0;
}

int main(int argc, char **argv) {
  init_nnom();
  nnom_model_t *model;
  model = nnom_model_create();
  if (model == nullptr) {
    std::cerr << "nnom_model_create failed\n";
    return -1;
  }
  model_run(model);
  validation_data_t val_data;
  // load_validation_bin("./test_data.bin", &val_data, kSampleSize);
  val_data.samples.push_back(std::vector<int8_t>(kSampleSize * 6));
  if (load_imu_dataset("dataset/v1/swingrightward_imu_data_0.txt",
                       val_data.samples.begin()->data(), kSampleSize * 6)) {
    printf("failed load_imu_dataset\n");
    return -1;
  }
  parse_val_data_imu(&val_data);
  int8_t *feed_data = val_data.samples.begin()->data();
  size_t feed_length = val_data.samples.begin()->size();
  feed_model_input(feed_data, feed_length);
  model_run(model);
  fetch_model_output_and_print();
  return 0;
}