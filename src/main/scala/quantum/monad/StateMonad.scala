package quantum.monad

trait StateMonad[S, A] {
  val run: S => (S, A)

  def apply(s: S): (S, A) =
    run(s)

  def eval(s: S): A =
    apply(s)._2

  def map[B](f: A => B): StateMonad[S, B] = StateMonad { s: S =>
    val (s1, a) = run(s)
    (s1, f(a))
  }

  def flatMap[B](f: A => StateMonad[S, B]): StateMonad[S, B] = StateMonad { s: S =>
    val (s1, a) = run(s)
    f(a)(s1)
  }

  def sequence[I](inputs: List[I], f: I => StateMonad[S, A]): StateMonad[S, List[A]] =
    StateMonad.sequence(List(this) ++ inputs.map(f))

}

object StateMonad {
  def apply[S, A](f: S => (S, A)): StateMonad[S, A] = new StateMonad[S, A] {
    final val run = f
  }

  def state[S, A](a: A): StateMonad[S, A] = StateMonad { s: S => (s, a) }
  def get[S]: StateMonad[S, S] = StateMonad { s: S => (s, s) }
  def gets[S, A](f: S => A): StateMonad[S, A] = StateMonad { s: S => (s, f(s)) }
  def modify[S](f: S => S): StateMonad[S, Unit] = StateMonad { s: S => (f(s), ()) }

  def map2[S, A, B, C](ma: StateMonad[S, A], mb: StateMonad[S, B])(f: (A, B) => C): StateMonad[S, C] =
    ma.flatMap(a => mb.map(b => f(a, b)))

  def sequence[S, A](lma: List[StateMonad[S, A]]): StateMonad[S, List[A]] =
    lma.foldRight(state[S, List[A]](List[A]()))((ma, mla) => map2[S, A, List[A], List[A]](ma, mla)(_ :: _))

  def chain[S, A](lma: List[StateMonad[S, A]]): StateMonad[S, A] =
    lma.foldRight(state[S, List[A]](List[A]()))((ma, mla) => map2[S, A, List[A], List[A]](ma, mla)(_ :: _)).map(_.last)


  def traverse[S, A, B](la: List[A])(f: A => StateMonad[S, B]): StateMonad[S, List[B]] =
    la.foldRight(state[S, List[B]](List[B]()))((a, mlb) => map2(f(a), mlb)(_ :: _))

}
