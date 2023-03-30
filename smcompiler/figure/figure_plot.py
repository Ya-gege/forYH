import matplotlib.pyplot as plt

# 设置全局字体
plt.rc('font', family='Times New Roman')

# 字体大小
font_size = 30

# 数据
party_num = [5, 10, 15, 20, 25, 30]
comm_cost_request_left = [1.428, 5.702, 12.834, 22.806, 35.632, 51.296]
comm_cost_response_left = [2.298, 10.310, 24.144, 43.686, 68.982, 100.016]

comm_cost_request_right = [1.428, 5.702, 12.834, 22.806, 35.632, 51.296]
comm_cost_response_right = [2.298, 10.310, 24.144, 43.686, 68.982, 100.016]

plt.figure(figsize=(17, 6))
ax = plt.subplot(121)

plt.plot(party_num, comm_cost_request_left, linewidth=3, color='r', label="Request", marker='o', markersize=8)
plt.plot(party_num, comm_cost_response_left, linewidth=3, color='b', label="Response", marker='v', markersize=8)

# 线标签放置在坐上方
plt.legend(loc="upper left", fontsize=font_size)

# 设置坐标轴标签字号
plt.xticks(fontsize=font_size)
plt.yticks(fontsize=font_size)

# 设置坐标轴标签大小
ax.set_xlabel(..., fontsize=font_size)
ax.set_ylabel(..., fontsize=font_size)

# 坐标轴标签
plt.xlabel("Number of party")
plt.ylabel("Comm-cost (kilo-bytes)")

ax = plt.subplot(122)
plt.plot(party_num, comm_cost_request_right, linewidth=3, color='r', label="Request", marker='o', markersize=8)
plt.plot(party_num, comm_cost_response_right, linewidth=3, color='b', label="Response", marker='v', markersize=8)

# 线标签放置在坐上方
plt.legend(loc="upper left", fontsize=font_size)

# 设置坐标轴标签字号
plt.xticks(fontsize=font_size)
plt.yticks(fontsize=font_size)

# 设置坐标轴标签大小
ax.set_xlabel(..., fontsize=font_size)
ax.set_ylabel(..., fontsize=font_size)

# 坐标轴标签
plt.xlabel("Number of party")
plt.ylabel("")
plt.ylim(0, 200)

plt.subplots_adjust(top=0.95, bottom=0.16, left=0.07, right=0.994, hspace=0, wspace=0.15)
# 保存文件
# plt.savefig('communication_cost_res_party_5_add_50.png', dpi=600)
plt.show()
