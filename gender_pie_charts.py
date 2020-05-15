import matplotlib.pyplot as plt

labels = 'Male', 'Female', 'Unknown'
entire_sizes = [4007, 1489, 936]
biology_sizes = [1049, 689, 142]
cs_sizes = [1312, 354, 136]
ee_sizes = [1424, 362, 601]
math_sizes = [285, 106, 62]

fig, ax = plt.subplots(3, 2)
ax[0][0].pie(entire_sizes, labels=labels, autopct='%1.1f%%', startangle=90)
ax[0][0].set_title('Entire Network')

ax[1][0].pie(biology_sizes, labels=labels, autopct='%1.1f%%', startangle=90)
ax[1][0].set_title('Biology')

ax[1][1].pie(cs_sizes, labels=labels, autopct='%1.1f%%', startangle=90)
ax[1][1].set_title('Computer Science')

ax[2][0].pie(ee_sizes, labels=labels, autopct='%1.1f%%', startangle=90)
ax[2][0].set_title('Electrical Engineering')

ax[2][1].pie(math_sizes, labels=labels, autopct='%1.1f%%', startangle=90)
ax[2][1].set_title("Mathematics")

ax[0][1].axis('off')

plt.savefig('./data/gender_pie_charts.jpg')
