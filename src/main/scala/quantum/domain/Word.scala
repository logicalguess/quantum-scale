package quantum.domain

case class Word(letters: List[Symbol])  {
  val label = letters.map(_.label).mkString

  override def toString: String = label
}

object Word {
  def apply(letters: Symbol*) = new Word(letters.toList)

  def fromInt(i: Int, width: Int): Word = {
    def helper(i: Int, width: Int, acc: List[Symbol]): List[Symbol] = {
      if (width == 0) acc
      else helper(i / 2, width - 1, (if (i % 2 == 0) S0 else S1) :: acc)
    }

    Word(helper(i, width, Nil))
  }

  def toInt(s: Word): Int = {
    def helper(ls: List[Symbol], acc: Int): Int = {
      ls match {
        case Nil => acc
        case S0 :: rest => helper(rest, acc * 2)
        case S1 :: rest => helper(rest, acc * 2 + 1)
      }
    }

    helper(s.letters, 0)
  }
}
