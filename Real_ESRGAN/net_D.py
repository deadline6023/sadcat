import torch.nn as nn
import torch.nn.functional as F
from torch.nn.utils import spectral_norm as norm

class Discriminator(nn.Module):
    def __init__(self):
        super(Discriminator, self).__init__()
        self.skip_connection = True

        num_in_ch = 3
        hidden_num = 64

        self.conv0 = nn.Conv2d(num_in_ch, hidden_num, kernel_size=3, stride=1, padding=1)

        # downsample
        self.conv1 = norm(nn.Conv2d(hidden_num, hidden_num * 2, kernel_size=4, stride=2, padding=1, bias=False))
        self.conv2 = norm(nn.Conv2d(hidden_num * 2, hidden_num * 4, kernel_size=4, stride=2, padding=1, bias=False))
        self.conv3 = norm(nn.Conv2d(hidden_num * 4, hidden_num * 8, kernel_size=4, stride=2, padding=1, bias=False))

        # upsample
        self.conv4 = norm(nn.Conv2d(hidden_num * 8, hidden_num * 4, kernel_size=3, stride=1, padding=1, bias=False))
        self.conv5 = norm(nn.Conv2d(hidden_num * 4, hidden_num * 2, kernel_size=3, stride=1, padding=1, bias=False))
        self.conv6 = norm(nn.Conv2d(hidden_num * 2, hidden_num * 1, kernel_size=3, stride=1, padding=1, bias=False))
        self.conv7 = norm(nn.Conv2d(hidden_num, hidden_num, kernel_size=3, stride=1, padding=1, bias=False))
        self.conv8 = norm(nn.Conv2d(hidden_num, hidden_num, kernel_size=3, stride=1, padding=1, bias=False))

        # output
        self.conv9 = nn.Conv2d(hidden_num, 1, kernel_size=3, stride=1, padding=1)

    def forward(self, x):
        # downsample
        x0 = F.leaky_relu(self.conv0(x), negative_slope=0.2, inplace=True)
        x1 = F.leaky_relu(self.conv1(x0), negative_slope=0.2, inplace=True)
        x2 = F.leaky_relu(self.conv2(x1), negative_slope=0.2, inplace=True)
        x3 = F.leaky_relu(self.conv3(x2), negative_slope=0.2, inplace=True)

        # upsample
        x3 = F.interpolate(x3, scale_factor=2, mode='bilinear', align_corners=False)
        x4 = F.leaky_relu(self.conv4(x3), negative_slope=0.2, inplace=True)

        if self.skip_connection:
            x4 = x4 + x2
        x4 = F.interpolate(x4, scale_factor=2, mode='bilinear', align_corners=False)
        x5 = F.leaky_relu(self.conv5(x4), negative_slope=0.2, inplace=True)

        if self.skip_connection:
            x5 = x5 + x1
        x5 = F.interpolate(x5, scale_factor=2, mode='bilinear', align_corners=False)
        x6 = F.leaky_relu(self.conv6(x5), negative_slope=0.2, inplace=True)

        if self.skip_connection:
            x6 = x6 + x0

        # extra convolutions
        out = F.leaky_relu(self.conv7(x6), negative_slope=0.2, inplace=True)
        out = F.leaky_relu(self.conv8(out), negative_slope=0.2, inplace=True)
        out = self.conv9(out)

        return out