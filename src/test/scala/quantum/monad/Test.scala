package quantum.monad


object Test {

  def main (args: Array[String] ): Unit = {
    val c = new ComponentMonad[Int, Int, Int] {
      override def logic: PartialFunction[(Int, Int), Int] = { case (i, j) => i + j }
      override def transformer: Function[Int, Int] = 2*_
    }

    var m = for {
      _ <- c.process(2)
      _ <- c.process(3)
      res <- c.process(5)
    } yield res

    println(m.run(1))

    val seqm = c.sequence(List(2, 3, 5))
    println("sequence: " + seqm.run(1))
    // (11,List(6, 12, 22))

    val trm = c.traverse(List(2, 3, 5))
    println("traverse: " + trm.run(1))
    // (11,List(6, 12, 22))

    val chainm = c.chain(List(2, 3, 5))
    println("chain: " + chainm.run(1))
    // (11, 22)


    val updm: StateMonad[Int, List[Unit]] = c.update(List(2, 3, 5))
    println("update: " + updm.run(1)._1)
    // 11

    val sum: (Int, Int, Int) => Int = _ + _ + _
    val sumCurried: Int => Int => Int => Int = sum.curried

    val f: Int => Int = sum.curried(1)(2)
    val g: Int => Int = sum(1, 2, _: Int)

    println(f(3)) //6
    println(g(3)) //6

    def factory[A](a: A): StateMonad[A => Any, Any] = {
      StateMonad[A => Any, Any] { f =>
        val g: A => Any = if (f(a).isInstanceOf[A => Any]) f(a).asInstanceOf[A => Any] else identity

        (g, f(a))
      }
    }

    val fm = StateMonad.traverse(List(2, 3, 5))(factory)
    println("traverse factory int: " + fm.run(sum.curried)._2)
    //traverse factory int: List(<function1>, <function1>, 10)

    val concat: (String, String, String) => String = _ + _ + _
    val fm1 = StateMonad.traverse(List("a", "b", "c"))(factory)
    println("traverse factory string: " + fm1.run(concat.curried)._2)
    //traverse factory string: List(<function1>, <function1>, abc)

    object fs {
      def comb(list: Any*): String = {
        list.mkString
      }

      def comb1(i: Int, s1: String, s2: String): String = i + s1 + s2

    }

    val args = List(2, "b", "c")
    println(fs.comb(args: _*))

    import scala.reflect.runtime.universe._
    val im = runtimeMirror(fs.getClass.getClassLoader).reflect(fs)

    val method = im.symbol.typeSignature.member(TermName("comb")).asMethod
    println("comb: " + im.reflectMethod(method)(args))

    val method1 = im.symbol.typeSignature.member(TermName("comb1")).asMethod
    println("comb1: " + im.reflectMethod(method1)(args: _*))

  }

}
