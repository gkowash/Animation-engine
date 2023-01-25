class ConstantRF:
    def get_ds(self, t, T):
        return 1


class LinearRF:
    def __init__(self, a, b):
        self.a = a
        self.b = b

    def get_ds(self, t, T): #left and right fractions are equal for this one, so a is just one number
        a = self.a
        b = self.b
        m = 2/(a*T*(2-a-b))
        if t < a*T:
            return (1/2)*m*t**2
        elif a*T <= t < T*(1-b):
            return m*a*T*t-(m/2)*(a*T)**2
        elif T*(1-b) <= t: #< T:
            return (-m*a/b)*((1/2)*t**2-T*t)+T*(1-m*a*T/(2*b)) #this one isn't working, need to rework the math


class SmoothMove:
    def __init__(self, a=1/4):
        self.a = a

    def get_ds(self, t, T):
        a = self.a
        ds_max = 1/(1-a)
        if t < a*T:
            return t/(a*T*(1-a))
        elif a*T <= t <= T-a*T:
            return 1/(1-a)
        elif t > T-a*T:
            return (T-t)/(a*T*(1-a))


class SlowStartSlowStop(SmoothMove):
    def __init__(self):
        SmoothMove.__init__(self, a=1/2)


class QuickStartQuickStop(SmoothMove):
    def __init__(self):
        SmoothMove.__init__(self, a=1/6)


class QuickStartSlowStop(LinearRF):
    def __init__(self):
        LinearRF.__init__(self, 1/4, 1/2)


class SlowStartQuickStop(LinearRF):
    def __init__(self):
        LinearRF.__init__(self, 1/2, 1/4)
