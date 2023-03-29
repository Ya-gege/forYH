import matplotlib.pyplot as plt

# 设置全局字体
plt.rc('font', family='Times New Roman')

# 字体大小
font_size = 14

# 数据
party_num = [5, 10, 15, 20, 25, 30]
comm_cost_request = [1428, 5702, 12834, 22806, 35632, 51296]
comm_cost_response = [2298, 10310, 24144, 43686, 68982, 100016]

plt.figure(figsize=(8, 5))
ax = plt.subplot(111)

plt.plot(party_num, comm_cost_request, linewidth = 3, color = 'r', label="Request", marker = 'o', markersize = 8)
plt.plot(party_num, comm_cost_response, linewidth = 3, color = 'b', label="Response", marker = 'v', markersize = 8)

# 线标签放置在坐上方
plt.legend(loc="upper left", fontsize = font_size)

# 设置坐标轴标签字号
plt.xticks(fontsize = font_size)
plt.yticks(fontsize = font_size)

# 设置坐标轴标签大小
ax.set_xlabel(..., fontsize = font_size)
ax.set_ylabel(..., fontsize = font_size)

# 坐标轴标签
plt.xlabel("Number of party")
plt.ylabel("Communication cost (bytes)")

# 保存文件
plt.savefig('communication_cost_res_party_5_add_50.png', dpi=600)

plt.show()
