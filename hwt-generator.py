import os
import wx
import wx.richtext as rt
import random
from PIL import Image, ImageDraw, ImageFont


def load_fonts(font_directory):
    fonts = []
    for file in os.listdir(font_directory):
        if file.endswith(".ttf") or file.endswith(".otf"):
            fonts.append(file)
    return fonts


class MyFrame(wx.Frame):
    def __init__(self, *args, **kw):
        super(MyFrame, self).__init__(*args, **kw)
        self.font_size = 20

        panel = wx.Panel(self)

        self.richTextCtrl = rt.RichTextCtrl(panel, style=wx.VSCROLL | wx.HSCROLL | wx.NO_BORDER)
        wx.CallAfter(self.richTextCtrl.SetFocus)

        button_sizer = wx.BoxSizer(wx.VERTICAL)

        button_row1_sizer = wx.BoxSizer(wx.HORIZONTAL)

        font_choices = load_fonts("./fonts")
        self.font_choice = wx.Choice(panel, choices=font_choices)
        self.font_choice.SetSelection(0)
        self.on_font_change(None)
        self.font_choice.Bind(wx.EVT_CHOICE, self.on_font_change)
        button_row1_sizer.Add(self.font_choice, 0, wx.ALL, 5)

        bold_button = wx.Button(panel, label='Bold')
        bold_button.Bind(wx.EVT_BUTTON, self.on_bold)
        button_row1_sizer.Add(bold_button, 0, wx.ALL, 5)

        underline_button = wx.Button(panel, label='Underline')
        underline_button.Bind(wx.EVT_BUTTON, self.on_underline)
        button_row1_sizer.Add(underline_button, 0, wx.ALL, 5)

        font_size_button = wx.Button(panel, label='Change Font Size')
        font_size_button.Bind(wx.EVT_BUTTON, self.on_font_size)
        button_row1_sizer.Add(font_size_button, 0, wx.ALL, 5)

        randomize_button = wx.Button(panel, label='Randomize')
        randomize_button.Bind(wx.EVT_BUTTON, self.on_randomize)
        button_row1_sizer.Add(randomize_button, 0, wx.ALL, 5)

        button_sizer.Add(button_row1_sizer, 0, wx.ALIGN_LEFT)

        button_row2_sizer = wx.BoxSizer(wx.HORIZONTAL)

        color_button = wx.Button(panel, label='Color')
        color_button.Bind(wx.EVT_BUTTON, self.on_color)
        button_row2_sizer.Add(color_button, 0, wx.ALL, 5)

        align_left_button = wx.Button(panel, label='Align Left')
        align_left_button.Bind(wx.EVT_BUTTON, lambda event: self.on_align(event, wx.TEXT_ALIGNMENT_LEFT))
        button_row2_sizer.Add(align_left_button, 0, wx.ALL, 5)

        align_center_button = wx.Button(panel, label='Align Center')
        align_center_button.Bind(wx.EVT_BUTTON, lambda event: self.on_align(event, wx.TEXT_ALIGNMENT_CENTER))
        button_row2_sizer.Add(align_center_button, 0, wx.ALL, 5)

        align_right_button = wx.Button(panel, label='Align Right')
        align_right_button.Bind(wx.EVT_BUTTON, lambda event: self.on_align(event, wx.TEXT_ALIGNMENT_RIGHT))
        button_row2_sizer.Add(align_right_button, 0, wx.ALL, 5)

        reset_styling_button = wx.Button(panel, label='Reset Styling')
        reset_styling_button.Bind(wx.EVT_BUTTON, self.on_reset_styling)
        button_row2_sizer.Add(reset_styling_button, 0, wx.ALL, 5)

        export_image_button = wx.Button(panel, label='Export to Image')
        export_image_button.Bind(wx.EVT_BUTTON, self.on_export_image)
        button_row2_sizer.Add(export_image_button, 0, wx.ALL, 5)

        button_sizer.Add(button_row2_sizer, 0, wx.ALIGN_LEFT)

        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(button_sizer, 0, wx.EXPAND)
        sizer.Add(self.richTextCtrl, 1, wx.EXPAND)
        panel.SetSizer(sizer)

    def on_reset_styling(self, event):
        style = rt.RichTextAttr()
        style.SetFontWeight(wx.FONTWEIGHT_NORMAL)
        style.SetFontUnderlined(False)
        style.SetTextColour(wx.BLACK)
        self.richTextCtrl.SetStyle(rt.RichTextRange(0, len(self.richTextCtrl.GetValue())), style)

    def on_export_image(self, event):
        lines = self.richTextCtrl.GetValue().split('\n')
        selected_font = self.font_choice.GetStringSelection()
        max_line_width = 0
        temp_image = Image.new("RGBA", (1, 1))
        temp_draw = ImageDraw.Draw(temp_image)

        for line_no, line in enumerate(lines):
            line_width = 0
            for char in line:
                font = ImageFont.truetype(f"./fonts/{selected_font}", self.font_size)
                char_width = temp_draw.textsize(char, font=font)[0]
                line_width += char_width

            max_line_width = max(max_line_width, line_width)

        images = []
        for line_no, line in enumerate(lines):
            image_height = int(self.font_size * 1.2)
            image = Image.new("RGBA", (max_line_width, image_height), (0, 0, 0, 0))
            draw = ImageDraw.Draw(image)
            x_offset = 0

            for char_no, char in enumerate(line):
                position = self.richTextCtrl.XYToPosition(char_no, line_no)
                style = rt.RichTextAttr()
                self.richTextCtrl.GetStyle(position, style)

                font = ImageFont.truetype(f"./fonts/{selected_font}", self.font_size)
                char_width = draw.textsize(char, font=font)[0]

                if style.GetFontWeight() == wx.FONTWEIGHT_BOLD:
                    draw.text((x_offset + 1, 5), char, font=font, fill="black")
                    draw.text((x_offset, 5), char, font=font, fill="black")
                elif style.GetFontUnderlined():
                    draw.text((x_offset, 5), char, font=font, fill="black")
                    underline_y = 5 + font.getsize(char)[1] + 1
                    draw.line([(x_offset, underline_y), (x_offset + char_width, underline_y)], fill="black",
                              width=int(self.font_size * 0.075))

                color = style.GetTextColour()
                color = (color.red, color.green, color.blue, 255)

                draw.text((x_offset, 5), char, font=font, fill=color)
                x_offset += char_width

            images.append(image)

        total_height = sum(image.height for image in images)
        final_image = Image.new("RGBA", (max_line_width, total_height), (0, 0, 0, 0))
        y_offset = 0
        for image in images:
            final_image.paste(image, (0, y_offset))
            y_offset += image.height

        final_image.save("output.png")

    def update_font(self):
        font_attr = rt.RichTextAttr()
        font_attr.SetFontSize(self.font_size)
        self.richTextCtrl.SetStyle(self.richTextCtrl.GetSelectionRange(), font_attr)

    def on_font_change(self, event):
        font_name = self.font_choice.GetStringSelection()
        font_attr = rt.RichTextAttr()
        font_attr.SetFontFaceName(font_name)
        self.richTextCtrl.SetStyle(self.richTextCtrl.GetSelectionRange(), font_attr)

    def on_bold(self, event):
        self.richTextCtrl.ApplyBoldToSelection()

    def on_italic(self, event):
        self.richTextCtrl.ApplyItalicToSelection()

    def on_underline(self, event):
        self.richTextCtrl.ApplyUnderlineToSelection()

    def on_font_size(self, event):
        dlg = wx.TextEntryDialog(self, 'Enter font size:', 'Change Font Size', str(self.font_size))
        if dlg.ShowModal() == wx.ID_OK:
            try:
                new_font_size = int(dlg.GetValue())
                if new_font_size > 0:
                    self.font_size = new_font_size
                    self.update_font()
            except ValueError:
                pass
        dlg.Destroy()

    def on_randomize(self, event):
        text = self.richTextCtrl.GetValue()
        words = text.split(' ')
        num_words = len(words)
        num_to_change = int(num_words * random.uniform(0.1, 0.5))  # change 10%-50% of words
        words_to_change = random.sample(range(num_words), num_to_change)

        position = 0
        for i, word in enumerate(words):
            if i in words_to_change:
                start = position
                end = start + len(word)

                attr = rt.RichTextAttr()
                if random.choice([True, False]):
                    attr.SetFontWeight(wx.FONTWEIGHT_BOLD)

                if random.choice([True, False]):
                    attr.SetFontUnderlined(True)

                color = wx.Colour(random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))
                attr.SetTextColour(color)

                self.richTextCtrl.SetStyle(rt.RichTextRange(start, end), attr)

            position += len(word) + 1

    def on_color(self, event):
        color_data = wx.ColourData()
        color_data.SetChooseFull(True)
        for i in range(0, 16):
            color_item = wx.Colour(i*16, i*16, i*16)
            color_data.SetCustomColour(i, color_item)

        dlg = wx.ColourDialog(self, color_data)

        if dlg.ShowModal() == wx.ID_OK:
            new_color_data = dlg.GetColourData()
            color = new_color_data.GetColour()
            color_attr = rt.RichTextAttr()
            color_attr.SetTextColour(color)
            self.richTextCtrl.SetStyle(self.richTextCtrl.GetSelectionRange(), color_attr)

        dlg.Destroy()

    def on_align(self, event, alignment):
        attr = rt.RichTextAttr()
        attr.SetAlignment(alignment)
        self.richTextCtrl.SetStyle(self.richTextCtrl.GetSelectionRange(), attr)


if __name__ == "__main__":
    app = wx.App()
    frm = MyFrame(None, title="RichTextCtrl Basic Style", size=(600, 600))
    frm.Show()
    app.MainLoop()
