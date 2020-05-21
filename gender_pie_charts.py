import matplotlib.pyplot as plt

labels = 'Male', 'Female', 'Unknown'
entire_sizes = [4007, 1489, 936]
biology_sizes = [1049, 689, 142]
cs_sizes = [1312, 354, 136]
ee_sizes = [1424, 362, 601]
math_sizes = [285, 106, 62]

fig, ax = plt.subplots(5, 2)
plt.subplots_adjust(hspace=2.5)

ax[0][0].pie(entire_sizes, radius=2.5, pctdistance=1.2, startangle=90, autopct='%1.1f%%')
ax[0][0].set_title('Entire Network', fontsize=10, y=1.7)

ax[1][0].pie(biology_sizes, radius=2.5, pctdistance=1.2, autopct='%1.1f%%', startangle=90)
ax[1][0].set_title('Biology', fontsize=10, y=1.7)

ax[2][0].pie(cs_sizes, radius=2.5, pctdistance=1.2, autopct='%1.1f%%', startangle=90)
ax[2][0].set_title('Computer Science', fontsize=10, y=1.7)

ax[3][0].pie(ee_sizes, radius=2.5, pctdistance=1.2, autopct='%1.1f%%', startangle=90)
ax[3][0].set_title('Electrical Engineering', fontsize=10, y=1.7)

ax[4][0].pie(math_sizes, radius=2.5, pctdistance=1.2, autopct='%1.1f%%', startangle=90)
ax[4][0].set_title("Mathematics", fontsize=10, y=1.7)

ax[0][1].axis('off')

cp_bio = [19, 24]
cp_cs = [35, 9]
cp_ee = [35, 4]
cp_math = [20, 10, 3]

ax[1][1].pie(cp_bio, radius=2.5, pctdistance=1.2, autopct='%1.1f%%', startangle=90)
ax[1][1].set_title('Biology (Cal Poly)', fontsize=10, y=1.7)

ax[2][1].pie(cp_cs, radius=2.5, pctdistance=1.2, autopct='%1.1f%%', startangle=90)
ax[2][1].set_title('Computer Science (Cal Poly)', fontsize=10, y=1.7)

ax[3][1].pie(cp_ee, radius=2.5, pctdistance=1.2, autopct='%1.1f%%', startangle=90)
ax[3][1].set_title('Electrical Engineering (Cal Poly)', fontsize=10, y=1.7)

ax[4][1].pie(cp_math, radius=2.5, pctdistance=1.2, autopct='%1.1f%%', startangle=90)
ax[4][1].set_title("Mathematics (Cal Poly)", fontsize=10, y=1.7)

fig.legend(labels)

plt.savefig('./data/gender_pie_charts.jpg')
