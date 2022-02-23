
Maximize
  obj: c_0 + c_1 + c_2

Subject To
  like_0_peppers: c_0 - i_0 <= 0
  like_0_cheese: c_0 - i_1 <= 0

  like_1_basil: c_1 - i_2 <= 0
  dislike_1_pineapple: c_1 + i_3 <= 1
  like_2_tomatoes: c_2 - i_4 <= 0
  like_2_mushrooms: c_2 - i_5 <= 0
  dislike_2_basil: c_2 + i_2 <= 1

Binaries
  c_0 c_1 c_2
  i_0 i_1 i_2 i_3 i_4 i_5

End
