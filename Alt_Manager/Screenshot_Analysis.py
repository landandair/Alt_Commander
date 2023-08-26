import os

from PIL import Image
import pickle

def make_dict_files(img: Image):
    white = (255, 255, 255)
    window_size = (800, 600)
    size = img.size
    img_to_window = lambda pos: (pos[0] * window_size[0]//size[0], pos[1] * window_size[1]//size[1])

    """Find color button positions"""
    color_selector_height = 0
    for y in range(1,size[1]):
        color = img.getpixel((10, size[1]-y))[:3]
        if color != white:
            color_selector_height = size[1] - y + 1
            break

    y_has_stuff = []
    for y in range(color_selector_height, size[1]):
        has_stuff = False
        for x in range(size[0]):
            color = img.getpixel((x, y))[:3]
            if color != white:
                has_stuff = True
        y_has_stuff.append(has_stuff)

    buttons = []
    for i, has_stuff in list(enumerate(y_has_stuff))[1:]:
        if not y_has_stuff[i-1] and has_stuff:  # button start
            buttons.append([])
            buttons[-1].append(i)
        elif y_has_stuff[i-1] and not has_stuff:  # Button stop
            buttons[-1].append(i)

    check_rows = []
    for dif in buttons:
        check_rows.append(sum(dif)//len(dif))

    started = False
    color_to_pos = {}
    start = 0
    for row in check_rows[:-1]:
        last_color = white
        for x in range(size[0]):
            pos = (x, row + color_selector_height)
            color = img.getpixel(pos)[:3]
            if color != last_color:
                if not started and color != white:
                    start = x
                    started = True
                elif color == white and color != last_color and x-start > 4 and started:
                    started = False
                    end = x
                    average_x = (start+end)//2
                    # print(start, end)
                    pos = (average_x, row + color_selector_height)
                    color = img.getpixel(pos)[:3]
                    if row != check_rows[-1]:  # This means it is not the confirm button
                        color_to_pos[color] = pos
            last_color = color

    last_color = white
    end = 'error'
    for x in range(size[0]):
        pos = (x, check_rows[-1] + color_selector_height)
        color = img.getpixel(pos)[:3]
        if last_color != color and last_color == white:
            start = x
        elif last_color != color and color == white:
            end = x
        last_color = color
    color_to_pos['place'] = img_to_window(((end+start)//2, check_rows[-1] + color_selector_height))
    print(f'{len(color_to_pos)-1} color buttons found')
    """Find movement offset to position dictionary (in pixel on screen position)"""
    # Manually place your cursor soundly in the select box of the center position of the screen
    # (use real screenshot from bot)
    # Dimensions given in screenshot pixel size
    # x, y(down)
    center = (800, 650)
    # Measure the width of a single pixel (this will be checked for accuracy so be as close as you can)
    block_width = 50
    # Desired offsets
    top_left = (-13, -6)
    bottom_right = (13, 3)
    bad_offsets = ((0, -1), (-1, -1), (1, -1))  # Mostly blocked by username
    offset_to_pos = {'border_moves': []}
    for x in range(top_left[0], bottom_right[0]+1):
        for y in range(top_left[1], bottom_right[1]+1):
            if (x, y) not in bad_offsets:
                offset_to_pos[(x, y)] = img_to_window((center[0] + block_width*x, center[1] + block_width*y))
                if x == top_left[0] or x == bottom_right[0] or y == top_left[1] or y == bottom_right[1]:  # Border
                    offset_to_pos['border_moves'].append((x, y))

    print(offset_to_pos)

    with open('Dictionaries/button_pos.pickle', 'wb') as fi:
        pickle.dump(color_to_pos, fi)
    with open('Dictionaries/movement_pos.pickle', 'wb') as fi:
        pickle.dump(offset_to_pos, fi)


if __name__ == '__main__':
    ref_image = os.getcwd() + '/screenshots/fake_user.png'
    img = Image.open(ref_image)
    make_dict_files(img)
