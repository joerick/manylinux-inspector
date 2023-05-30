# Manylinux Inspector

<img width="1333" alt="image" src="https://github.com/joerick/manylinux-inspector/assets/1244307/20dc9f61-e452-4e7b-a9c7-b22bb227e671">

[This website](https://manylinuxinspector.joerick.me/) provides an overview of the images created by the [manylinux project](https://github.com/pypa/manylinux).

Manylinux (and musllinux) images are the easiest way to build Python wheels that work on nearly every linux-based operating systems.

Because they're constantly kept up-to-date, with newer operating systems, tools, and the latest versions of Python, it can be hard to know what's under the hood, and what's changed between versions. _Manylinux Inspector_ makes it easy to see what's installed on each image, and to spot the differences between images.

## How does it work?

The data in this site comes from a scheduled Github Action, which runs daily to:

- check the various repositories at quay.io to see if there's a new image
- for each new image, pulls it down with Docker and runs [loads of commands](https://github.com/joerick/manylinux-inspector/blob/main/inspect_image.py) to ask questions about it
- saves that information into the Github repo
- rebuilds the site, and redeploys it to Github Pages.

The frontend site is a Typescript/Vue.js app which loads the output of the inspection phase, parses it and displays the information.

All the code is open-source and on Github!
