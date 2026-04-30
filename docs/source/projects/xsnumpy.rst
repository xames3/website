.. Author: Akshay Mestry <xa@mes3.dev>
.. Created on: 01 March, 2025
.. Last updated on: 29 April, 2026

:og:title: Why write xsNumPy?
:og:description: Journey of building a lightweight, pure-python implementation
    of NumPy's core features
:og:type: article
:og:image: https://i.imgur.com/BPxkNzC.jpeg
:prompt: Have you rebuilt something just to learn?
:promptdesc: If you've cracked open an industry standard to truly master
    it, I'd love to hear your experiences.
:submitbtn: Share your "aha" moment

.. _project-building-xsnumpy:

===============================================================================
:fas:`at far` Why write xsNumPy?
===============================================================================

.. rst-class:: lead

    How writing a simplified NumPy in pure-Python taught me more about
    numerical computing than using the real thing.

.. author:: @xames3
    :avatar: https://avatars.githubusercontent.com/u/90549089?v=4
    :target: https://github.com/xames3

I'm a wee bit fuzzy on the exact timelines, but it all started around
mid-November of 2024. I was still at the uni and in my second-to-last quarter.
I was working on an assignment that required me to use
`NumPy`_.

I multiplied some matrices; NumPy did its thing, as it always does, and made
all the computations look super easy. But, under this "simplicity", a few
questions began to gnaw at me.

So, I thought of experimenting with a simple code, nothing fancy:

.. code-block:: python
    :linenos:

    a = np.array([[1, 2], [3, 4]])
    b = np.array([[5, 6], [7, 8]])
    np.dot(a, b)

The result popped out instantly. But this time, instead of just accepting the
answer, I asked myself a bunch of questions. Like, why was I even using
:func:`np.dot(a, b) <numpy.dot>` when I could've used
:py:data:`np.matmul(a, b) <numpy.matmul>`, which feels more appropriate?

And if :func:`np.dot(a, b) <numpy.dot>` indeed performs matrix multiplication,
then what's the deal with the :python:`a @ b` (:meth:`@ <object.__matmul__>`
operator)? Why are there three different ways to perform matrix multiplication,
and if so, which one's the best?

.. _building-with-a-purpose:

-------------------------------------------------------------------------------
Building with a purpose.
-------------------------------------------------------------------------------

With all these questions in mind, I was motivated enough to learn the actual
implementation details of NumPy. I was ready to build my own scrappy version. I
didn't set out to create something that'd rival NumPy; I mean, NumPy's a bloody
powerhouse, built over decades of work by incredibly talented minds in maths
and science, plus loads of optimisations.

I couldn't possibly compete with that.

I wanted to stop treating these libraries (starting with NumPy) as black boxes
and truly understand the "whys" and "hows". This realisation hit me so hard, I
challenged myself.

Could I build a dinky version of NumPy from scratch? Because if I'm going to
teach these concepts one day, I have to go **deeper**. If I were going to learn
this properly, I needed discipline and some rules to follow.

.. admonition:: :fas:`badge-check green` Rules of engagement
    :class: unusual-one note

    - No use of LLMs or any AI usage of anything.
    - Every line of code and every solution had to come from my own
      understanding and experimentation.
    - Pure Python only. No external dependencies, just the standard library.
    - It should be clean, maintainable, statically typed, and well-documented
      code that mirrors NumPy's public APIs, aiming to be a drop-in replacement
      where sensible.

.. _writing-my-first-array:

-------------------------------------------------------------------------------
Writing my first array.
-------------------------------------------------------------------------------

Now that I have set my rules, I started experimenting with NumPy's core APIs,
trying to understand their core behaviours and functionality. As I read through
more and more `documentation`_ and Stack Overflow answers, it quickly became
clear that most of NumPy's APIs are heavily relying on a single core construct,
the :func:`np.array <numpy.array>` function.

It's also worth noting that this function is a cheeky little wrapper for the
:class:`np.ndarray <numpy.ndarray>` class. That's where I decided to start,
implementing my own |xp.ndarray|_ data structure.

.. admonition:: :fas:`lightbulb` Quick analogy
    :class: unusual-one seealso

    If you're new to arrays, think of them as egg cartons, each slot holds an
    egg, and the shape of the carton tells you how many eggs you've got.

    Where your hand moves from one slot to the next are the strides; the type
    of eggs is the dtype; the carton itself is the buffer or the actual
    storage.

Now, by this point in time, I had a basic understanding of arrays and how they
worked. But, as I looked deeper and deeper, I discovered heaps of concepts,
including `memory allocation`_, `shape`_ calculations, `strides`_, and various
optimisation techniques for data storage.

It felt like opening Pandora's box; I wasn't ready. After a few days of
head-scratching, I managed to create a primitive, albeit minimal, working
version using Python's built-in :py:mod:`ctypes` module.

It worked poorly. But it worked!!

.. code-block:: python
    :caption: :fas:`file far` `xsnumpy/_core.py`_
    :linenos:

    class ndarray:

        def __init__(
            self, shape, dtype=None, buffer=None, offset=0, strides=None
        ):
            if not isinstance(shape, Iterable):
                shape = (shape,)
            self._shape = tuple(int(dim) for dim in shape)
            if dtype is None:
                dtype = globals()[dtype]
            self._dtype = dtype
            self._itemsize = int(_convert_dtype(dtype, "short")[-1])
            if buffer is None:
                self._base = None
                if self._offset != 0:
                    raise ValueError("Offset must be 0 when buffer is None")
                if strides is not None:
                    raise ValueError("Buffer is None; strides must be None")
                self._strides = calc_strides(self._shape, self.itemsize)
            else:
                if isinstance(buffer, ndarray) and buffer.base is not None:
                    buffer = buffer.base
                self._base = buffer
                if isinstance(buffer, ndarray):
                    buffer = buffer.data
                if self._offset < 0:
                    raise ValueError("Offset must be non-negative")
                if strides is None:
                    strides = calc_strides(self._shape, self.itemsize)
                elif not (
                    isinstance(strides, tuple)
                    and all(isinstance(stride, int) for stride in strides)
                    and len(strides) == len(self._shape)
                ):
                    raise ValueError("Invalid strides provided")
                self._strides = tuple(strides)
            buffersize = self._strides[0] * self._shape[0] // self._itemsize
            buffersize += self._offset
            Buffer = _convert_dtype(dtype, "ctypes") * buffersize
            if buffer is None:
                if not isinstance(Buffer, str):
                    self._data = Buffer()
            elif isinstance(buffer, ctypes.Array):
                self._data = Buffer.from_address(ctypes.addressof(buffer))
            else:
                self._data = Buffer.from_buffer(buffer)

.. rubric:: Keeping things simple.
.. rubric::
    I've intentionally removed loads of details to keep things simple. Check
    out the complete implementation of **ndarray** on GitHub.
    :class: subtitle-text

.. button:: https://github.com/xames3/xsnumpy/blob/main/xsnumpy/_core.py
    :faicon: fab fa-github

    See full implementation

.. rubric:: Making sense of shapes.
.. rubric::
    A shape of an array is a tuple of integers that represents the number of
    elements along **each dimension** (axis) of the array.
    :class: subtitle-text

I started by checking if the provided shape can be
:py:class:`iterated <collections.abc.Iterable>`. If it wasn't, I wrapped it in
a :py:class:`tuple`. Then, I converted the shape into a tuple of
:py:class:`integers <int>`, because you can't have non-integer dimensions in an
array.

.. code-block:: python
    :linenos:

    if not isinstance(shape, Iterable):
        shape = (shape,)
    self._shape = tuple(int(dim) for dim in shape)

Next up, the ``dtype`` (short for data type). If you didn't provide it the
constructor would default it to :py:obj:`None`. If a :py:class:`float` or an
:py:class:`int` is provided, it dynamically retrieves the appropriate data
type using the :func:`globals` namespace. This nifty trick meant I could
dynamically fetch whatever data type I fancied.

.. code-block:: python
    :linenos:

    if dtype is None:
        dtype = globals()[dtype]
    self._dtype = dtype

Right, on to the ``buffer``. If no ``buffer`` was provided, the array was
initialised without an external memory buffer. In this case, the ``offset``
must be zero, and the ``strides`` must be :py:obj:`None`. The constructor would
then calculate the `strides`_, which, put simply, are just the number of bytes
between consecutive elements in memory.

.. code-block:: python
    :linenos:

    if buffer is None:
        self._base = None
        if self._offset != 0:
            raise ValueError("Offset must be 0 when buffer is None")
        if strides is not None:
            raise ValueError("Buffer is None; strides must be None")
        self._strides = calc_strides(self._shape, self.itemsize)

But what if a buffer was provided?

Well, then it got trickier. It used the base buffer, and the strides were
either given directly or calculated.

.. code-block:: python
    :linenos:
    :emphasize-lines: 8

    else:
        if isinstance(buffer, ndarray) and buffer.base is not None:
            buffer = buffer.base
        self._base = buffer
        if isinstance(buffer, ndarray):
            buffer = buffer.data
        if strides is None:
            strides = calc_strides(self._shape, self.itemsize)
        self._strides = tuple(strides)

Finally, calculating the total ``buffer`` size. This was worked out using the
strides, shape, and the size. The ``buffer`` itself was a type derived from
the data type and its size. Depending on whether a buffer was passed or not,
the constructor handled it accordingly, either creating a new buffer or using
the existing one.

That's a lot of work, innit?

.. _illusion-of-simplicity:

-------------------------------------------------------------------------------
Illusion of simplicity.
-------------------------------------------------------------------------------

After all that hard work, I thought of giving myself a break. I remembered
telling myself

.. epigraph::

    Let's start with something dead easy... perhaps just display
    the array. That couldn't be hard, right? All I've to do is print the
    content of my array in a readable format, just like NumPy does

    -- silly me, *2025*

Little did I know, I was shooting myself in the foot. At its core, a
:meth:`__repr__ <object.__repr__>` is an object's internal data representation.
I started with something simple, and it worked for scalars and 1D arrays.

.. code-block:: python
    :linenos:

    def __repr__(self):
        return f"array({self._data}, dtype={str(self.dtype)})"

Feeling quite pleased and a bit cocky, I tried a 2D array, but it unexpectedly
printed everything as a flat list. I realised I hadn't accounted for the rows
and columns. No problem, I updated the code, and it worked.

.. code-block:: python
    :linenos:

    def __repr__(self):
        if self.ndim == 1:
            return f"array({self._data}, dtype={str(self.dtype)})"
        elif self.ndim > 1:
            rows = ",\n       ".join(
                [f"[{', '.join(map(str, row))}]" for row in self._data]
            )
            return f"array([{rows}], dtype={str(self.dtype)})"

Then the 3D arrays... It broke again.

That's when it hit me, this wasn't just about formatting strings. I needed a
general solution that would work with any number of dimensions. A few days
later, I found myself neck-deep in recursive logic and multidimensional
`indexing`_, all for what I believed was an "easy" print function.

What started as a chilled attempt to rework :meth:`__repr__ <object.__repr__>`
turned out to be a masterclass in designing for generality. This struggle
taught me something fundamental. What seemingly appears simple on the surface
often hides massive complexity underneath.

And so, I realised, printing a NumPy array from scratch was a rabbit hole.

.. seealso::

    Complete implementation of |xp.ndarray.repr|_ with helper functions.

.. rubric:: More than meets the eye.

After wrestling with the "simple" things, I naively believed the hardest part
was behind me. I was excited for the fun stuff: element-wise arithmetic,
`broadcasting`_, transposing, and other random functions. However, I didn't
realise my journey was about to get even more challenging.

Basic arithmetic operations like addition, subtraction, and scalar
multiplication seemed straightforward. I figured I could just iterate through
my flattened data and perform operations element-wise.

And it worked for the first few test cases. But, as always, the test cases
failed almost immediately for higher-dimensional vectors.

.. code-block:: python
    :linenos:
    :emphasize-lines: 4,11

    def __add__(self, other):
        arr = ndarray(self.shape, self.dtype)
        if isinstance(other, (int, float)):
            arr[:] = [x + other for x in self._data]
        elif isinstance(other, ndarray):
            if self.shape != other.shape:
                raise ValueError(
                    "Operands couldn't broadcast together with shapes "
                    f"{self.shape} {other.shape}"
                )
            arr[:] = [x + y for x, y in zip(self.flat, other.flat)]
        else:
            raise TypeError(
                f"Unsupported operand type(s) for +: {type(self).__name__!r} "
                f"and {type(other).__name__!r}"
            )
        return arr

What if I added a scalar to a matrix, or a ``(3,)`` array to a ``(3, 3)``
matrix? Could I add a :py:class:`float` to an :py:class:`int`? Each of those
experiments brought new challenges, and I was absolutely frustrated!!

That's when I realised I wasn't just adding or multiplying numbers, but
learning and simultaneously recreating NumPy's broadcasting rules.

.. rubric:: Final boss, Matrix Multiplication.
.. rubric:: Matrix multiplication was another **beast** entirely.
    :class: subtitle-text

I thought it would be just a matter of looping through rows and columns,
summing them element-wise, high school maths, if you ask me. And it worked as
well until I tried with higher-dimensional arrays.

This is where I realised that matrix multiplication isn't just about rows and
columns, but about correctly handling batch dimensions for higher-order
tensors.

I found myself diving into NVIDIA's documentation, reading about the
`Generalised Matrix Multiplication (GEMM)`_ routines and how broadcasting
affects the output shapes.

.. seealso::

    Complete implementation of `arithmetic operations
    <https://github.com/xames3/xsnumpy/blob/main/xsnumpy/_core.py>`_ on GitHub.

.. rubric:: Small victories, big lessons.
.. rubric::
    Here comes December. By now, I wasn't just rebuilding a scrappy numerical
    computing **doppelganger** like I thought I was.
    :class: subtitle-text

I was on my winter break. I was fully committed to this project because I
didn't have to attend uni or work on any assignments. After days of debugging,
I realised that my vector operations weren't just about getting the "maths"
right.

They were about thinking like NumPy:

- How can I minimise unnecessary data duplication?
- How can I broadcast arrays?
- How can I infer the correct output shape?

I was creating a flexible and extensible system that could handle both
intuitive and weird edge cases. With each iteration, every commit I made, I
explored even more ways to optimise it, reducing redundant calculations.

Every bug, every unexpected result, every failure, every new piece of answer
and advice that I received on Stack Overflow, and every small achievement
taught me something new about NumPy. As time passed, xsNumPy evolved into more
than just a project and a scrappy experiment.

It became a weird, obsessive mentality. A belief that the best way to learn is
by rolling up your sleeves, taking things apart, trying to understand the
problem, and putting it back together, piece by piece.

.. _so-what-can-xsnumpy-do:

-------------------------------------------------------------------------------
So, what can xsNumPy do?
-------------------------------------------------------------------------------

Like I said, xsNumPy started off as a learning exercise and has since grown
into a small but cheeky, reliable companion that I can use to demonstrate the
underlying mechanics of some of the implementations of NumPy.

It was not about speed but about clarity. Below are some things that xsNumPy
does quite well.

.. tab-set::

    .. tab-item:: :fas:`empty-set far` Creations

        xsNumPy provides familiar ways to create arrays. These creation
        routines are consistent, predictable, and designed to slot neatly into
        later operations.

        - ``array()``

          Like NumPy, the |xp.array|_ function is the bread and butter of
          xsNumPy as well. It's the most flexible way to create arrays from
          Python lists or tuples with sensible ``dtype`` inference and the
          option to set one explicitly.

          .. code-block:: python

              >>> import xsnumpy as xp
              >>> xp.array([[[1, 2], [3, 4]], [[5, 6], [7, 8]]])
              array([[[1, 2],
                      [3, 4]],

                     [[5, 6],
                      [7, 8]]])
              >>> xp.array([1, 0, 2], dtype=xp.bool)
              array([True, False, True])

        - ``zeros()``, ``ones()``, and ``full()``

          xsNumPy support |xp.zeros|_, |xp.ones|_, and |xp.full|_ functions for
          repeatable initialisation of arrays filled with, zeros, ones, and any
          ``fill_value`` respectively.

          .. code-block:: python

              >>> xp.zeros(3)
              array([0. , 0. , 0. ])
              >>> xp.ones([3, 2], dtype=xp.int32)
              array([[1, 1],
                     [1, 1],
                     [1, 1]])
              >>> xp.full(2, 3, fill_value=3.14159)
              array([[3.14159, 3.14159, 3.14159],
                     [3.14159, 3.14159, 3.14159]])

        - ``arange()``

          Inspired by Python's :py:class:`range`, |xp.arange|_ generates arrays
          with evenly spaced values.

          .. code-block:: python

              >>> xp.arange(0, 5, 0.5)
              array([0. , 0.5, 1. , 1.5, 2. , 2.5, 3. , 3.5, 4. , 4.5])

        .. seealso::

            Check out all of array `creation <https://github.com/xames3/
            xsnumpy?tab=readme-ov-file#array-creation-routines>`_ methods
            supported by xsNumPy on GitHub.

    .. tab-item:: :fas:`plus-minus far` Operations

        xsNumPy provides a range of arithmetic operations, carefully adhering
        to NumPy's rules for broadcasting and type coercion. The emphasis is on
        correctness and clear behaviour across dimensions.

        - **Element-wise arithmetic**

          xsNumPy supports element-wise addition, subtraction, multiplication,
          and division along with other basic arithmetics.

          .. code-block:: python

              >>> a = xp.array([[1, 0], [0, 1]])
              >>> b = xp.array([[4, 1], [2, 2]])
              >>> a + b
              array([[5, 1],
                     [2, 3]])

        - **Broadcasting arithmetic**

          xsNumPy matches shapes, stretches smaller arrays, and makes sure the
          output shape followed NumPy's exact logic. Just like NumPy, these
          operations are broadcasted.

          .. code-block:: python

              >>> matrix = xp.array([[1, 2, 3], [4, 5, 6], [7, 8, 9]])
              >>> vector = xp.array([[1], [2], [3]])
              >>> matrix + vector
              array([[ 2,  4,  6],
                     [ 5,  7,  9],
                     [ 8, 10, 12]])

        - **Linear algebraic helper functions**

          To mirror NumPy's API, xsNumPy supports explicit arithmetic
          functions. These are useful when you want to be very clear about the
          operation being performed or when you need more control over the
          parameters.

          .. code-block:: python

              >>> a = xp.array([[1, 0], [0, 1]])
              >>> b = xp.array([[4, 1], [2, 2]])
              >>> xp.dot(a, b)
              array([[4, 1],
                     [2, 2]])

        - **Scalar operations**

          xsNumPy supports scalar operations as well so you're not just
          limited to array-to-array operations.

          .. code-block:: python

              >>> xp.array([3, 4]) + 10
              array([13, 14])

        .. seealso::

            Check out examples of the arithmetic
            `operations <https://github.com/xames3/xsnumpy?
            tab=readme-ov-file#linear-algebra>`_ supported by xsNumPy on
            GitHub.

    .. tab-item:: :fas:`diagram-predecessor far` Transforms

        xsNumPy provides essential shape manipulation APIs that are predictable
        and memory-aware. The emphasis is on clarity of intent and avoiding
        unnecessary data duplication. Think of this as learning to fold and
        unfold the same fabric without tearing it.

        .. tip::

            Read more about `NumPy internals`_ here.

        - ``.reshape()``

          The |xp.ndarray.reshape|_ method changes the view of data when
          possible, preserving the total element count.

          .. code-block:: python

              >>> a = xp.array([1, 2, 3, 4, 5, 6])
              >>> a.reshape((2, 3))
              array([[1, 2, 3],
                     [4, 5, 6]])

        - ``.transpose()``

          Transposing is more than just flipping rows and columns; for
          higher-dimensional arrays, it's about permuting the axes. The
          |xp.ndarray.transpose|_ method does just that.

          .. code-block:: python

              >>> a = xp.array([[1, 2, 3], [4, 5, 6]])
              >>> a.transpose()
              array([[1, 4],
                     [2, 5],
                     [3, 6]])

        - ``.flatten()``

          The |xp.ndarray.flatten|_ method returns a tidy 1D copy.

          .. code-block:: python

              >>> a = xp.array([[1, 2, 3], [4, 5, 6]])
              >>> a.flatten()
              array([1, 2, 3, 4, 5, 6])

    .. tab-item:: :fas:`brackets-square far` Indexing

        Indexing is expressive and disciplined in xsNumPy, just like NumPy. The
        goal is to provide intuitive access to elements and subarrays while
        maintaining clarity about the underlying data structure.

        .. attention::

            Indexing and slicing were implemented by overridding the standard
            :meth:`__getitem__ <object.__getitem__>`  and
            :meth:`__setitem__ <object.__setitem__>`  protocols.

        - **Basic indexing**

          At its core, basic indexing in xsNumPy works similarly to NumPy,
          using zero-based indices to access elements. You can fetch single
          elements or entire subarrays. You can also use negative indices to
          count from the end of an array.

          .. code-block:: python

              >>> a = xp.array([[1, 2, 3], [4, 5, 6], [7, 8, 9]])
              >>> a[1, 2]
              6
              >>> a[-1, -2]
              8

        - **Slicing**

          Slicing allows you to extract subarrays using a
          :python:`a[start:stop:step]` format. Just like NumPy, xsNumPy
          supports almost all the classic slicing mechanics.

          .. code-block:: python

              >>> a = xp.array([[1, 2, 3], [4, 5, 6], [7, 8, 9]])
              >>> a[::2]
              array([[1, 2, 3],
                     [7, 8, 9]])
              >>> a[:2, 1:]
              array([[2, 3],
                     [5, 6]])

        - **Boolean masking**

          Boolean masking lets you select elements based on a condition.

          .. code-block:: python

              >>> a[a % 2 == 0]
              array([1, 2, 3])

        .. seealso::

            Check out the complete implementation
            `here <https://github.com/xames3/xsnumpy/blob/
            69c302ccdd594f1d8f0c51dbe16346232c39047f/xsnumpy/_core.py>`_
            on GitHub.

    .. tab-item:: :fas:`sigma far` Reductions

        Reductions condense information carefully, preserving the essence of
        the data. xsNumPy provides a few key reduction operations that are
        predictable and consistent.

        - ``.sum()``

          The |xp.sum|_ method computes the sum of elements along a given
          axis.

          .. code-block:: python

              >>> a = xp.array([[1, 2, 3], [4, 5, 6]])
              >>> a.sum()
              21
              >>> a.sum(axis=0)
              array([5, 7, 9])

        - ``.prod()``

          The |xp.prod|_ (product) method computes the multiplication of
          elements along a given axis.

          .. code-block:: python

              >>> a = xp.array([[1, 2, 3], [4, 5, 6]])
              >>> a.prod()
              720
              >>> a.prod(axis=0)
              array([ 4, 10, 18])

        - ``.any()`` and ``.all()``

          The |xp.all|_ method checks if all elements are :py:obj:`True`, while
          |xp.any|_ checks if at least one is.

          .. code-block:: python

              >>> b = xp.array([[True, False, True], [True, True, False]])
              >>> b.all()
              False
              >>> b.any(axis=1)
              array([True, True])


.. rubric:: Sharing notes with the community.
.. rubric::
    I gave a talk at `ChiPy`_ titled **"xsNumPy: Curiosity to Code"**, walking
    through the decisions, the missteps, and the insights that stayed with me.
    :class: subtitle-text

.. youtube:: https://www.youtube.com/watch?v=QIhyix3oEns
    :caption: The presentation covered the technical challenges, mathematical
        discoveries, and most importantly, the mindset shift from viewing
        libraries as opaque entities to understanding them as collections of
        elegant algorithms waiting to be explored.

.. _looking-back-moving-forward:

-------------------------------------------------------------------------------
Looking back, moving forward.
-------------------------------------------------------------------------------

xsNumPy didn't aim for performance; that wasn't the plan anyway. It was to
learn and understand, build intuition. It taught me to replace awe with
attention, trusting libraries while still learning and understanding their
core concepts with care.

Most importantly, it reminded me that doing something by yourself is perhaps
the best teaching and learning experience.

I intend to work on this project in small, respectful steps whenever I get
time. However, the larger work is already done. I re-learnt the essentials by
making them, and that learning will travel with me far beyond this code.

.. _NumPy: https://numpy.org
.. _Generalised Matrix Multiplication (GEMM): https://docs.nvidia.com/
    deeplearning/performance/dl-performance-matrix-multiplication/index.html
.. _multiplying matrices: https://www.mathsisfun.com/algebra/
    matrix-multiplying.html
.. _memory allocation: https://numpy.org/doc/stable/reference/
    c-api/data_memory.html
.. _shape: https://numpy.org/doc/stable/reference/generated/numpy.ndarray.
    shape.html
.. _strides: https://numpy.org/doc/stable/reference/generated/numpy.ndarray.
    strides.html
.. _broadcasting: https://numpy.org/doc/stable/user/basics.broadcasting.html
.. _indexing: https://numpy.org/doc/stable/user/basics.indexing.html
.. _NumPy internals: https://numpy.org/doc/stable/dev/internals.html
.. _ChiPy: https://www.chipy.org/
.. _documentation: https://numpy.org/doc/stable/reference/index.html#reference

.. _xsnumpy/_core.py: https://github.com/xames3/xsnumpy/blob/main/xsnumpy/
    _core.py

.. |xp.ndarray| replace:: ``ndarray``
.. _xp.ndarray: https://github.com/xames3/xsnumpy/blob/
    69c302ccdd594f1d8f0c51dbe16346232c39047f/xsnumpy/_core.py
.. |xp.ndarray.repr| replace:: ``__repr__``
.. _xp.ndarray.repr: https://github.com/xames3/xsnumpy/blob/
    69c302ccdd594f1d8f0c51dbe16346232c39047f/xsnumpy/_core.py
.. |xp.array| replace:: ``array``
.. _xp.array: https://github.com/xames3/xsnumpy/blob/
    69c302ccdd594f1d8f0c51dbe16346232c39047f/xsnumpy/_numeric.py
.. |xp.zeros| replace:: ``zeros``
.. _xp.zeros: https://github.com/xames3/xsnumpy/blob/
    69c302ccdd594f1d8f0c51dbe16346232c39047f/xsnumpy/_numeric.py
.. |xp.ones| replace:: ``ones``
.. _xp.ones: https://github.com/xames3/xsnumpy/blob/
    69c302ccdd594f1d8f0c51dbe16346232c39047f/xsnumpy/_numeric.py
.. |xp.full| replace:: ``full``
.. _xp.full: https://github.com/xames3/xsnumpy/blob/
    69c302ccdd594f1d8f0c51dbe16346232c39047f/xsnumpy/_numeric.py
.. |xp.arange| replace:: ``arange``
.. _xp.arange: https://github.com/xames3/xsnumpy/blob/
    69c302ccdd594f1d8f0c51dbe16346232c39047f/xsnumpy/_numeric.py
.. |xp.ndarray.reshape| replace:: ``reshape``
.. _xp.ndarray.reshape: https://github.com/xames3/xsnumpy/blob/
    69c302ccdd594f1d8f0c51dbe16346232c39047f/xsnumpy/_core.py
.. |xp.ndarray.transpose| replace:: ``transpose``
.. _xp.ndarray.transpose: https://github.com/xames3/xsnumpy/blob/
    69c302ccdd594f1d8f0c51dbe16346232c39047f/xsnumpy/_core.py
.. |xp.ndarray.flatten| replace:: ``flatten``
.. _xp.ndarray.flatten: https://github.com/xames3/xsnumpy/blob/
    69c302ccdd594f1d8f0c51dbe16346232c39047f/xsnumpy/_core.py
.. |xp.sum| replace:: ``sum``
.. _xp.sum: https://github.com/xames3/xsnumpy/blob/
    69c302ccdd594f1d8f0c51dbe16346232c39047f/xsnumpy/_numeric.py
.. |xp.prod| replace:: ``prod``
.. _xp.prod: https://github.com/xames3/xsnumpy/blob/
    69c302ccdd594f1d8f0c51dbe16346232c39047f/xsnumpy/_numeric.py
.. |xp.all| replace:: ``all``
.. _xp.all: https://github.com/xames3/xsnumpy/blob/
    69c302ccdd594f1d8f0c51dbe16346232c39047f/xsnumpy/_numeric.py
.. |xp.any| replace:: ``any``
.. _xp.any: https://github.com/xames3/xsnumpy/blob/
    69c302ccdd594f1d8f0c51dbe16346232c39047f/xsnumpy/_numeric.py
