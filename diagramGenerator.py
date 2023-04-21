import matplotlib
from matplotlib import pyplot as plt

class Diagram:
        def bebra(self, sum):
                matplotlib.use('agg')
                cards = [
                        'уверенность',
                        'малодушие'
                ]
                fig = plt.figure(figsize=(10, 7))
                plt.pie(sum, labels=cards)
                plt.savefig("bebra.png")

