FROM debian:bookworm

# Set labels to provide metadata about the container, indicating its purpose as a devcontainer for 3D Slicer development
LABEL org.opencontainers.image.title="TCIA Data Augmentation Container" \
      org.opencontainers.image.description="A toolbox container for data augmentation of TCAI data for deep-learning purposes." \
      maintainer="Rafael Palomar (rafael.palomar@ous-research.no)"

# Avoid prompts from apt
ENV DEBIAN_FRONTEND=noninteractive

# Copy the 'extra-packages' file containing the list of packages to be installed
COPY extra-packages /

# Update and install dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends $(grep -v '^#' /extra-packages) && \
    # Clean up to reduce the image size
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Install python dependencies
COPY pip-packages /
RUN grep -v '^#' /pip-packages | xargs pip install --break-system-packages
RUN rm /pip-packages

#Download and  install NBIA download client
RUN curl -LO https://github.com/CBIIT/NBIA-TCIA/releases/download/DR-4_4_3-TCIA-20240916-1/nbia-data-retriever_4.4.3-1_amd64.deb && \
    dpkg -x nbia-data-retriever_4.4.3-1_amd64.deb /

# Download and unpack Slicer
RUN curl -L https://slicer-packages.kitware.com/api/v1/file/hashsum/SHA512/de2b0e69b53a5f9db8328f5b7d2ac82d71bfff1ce3e380455a4624483c0f0c22a12c1d1027be5189b9af4b54174ce4cddae26146c0738e713dbd6c47404dd8dd/download | tar xz -C /opt

#Download Slicer-SOFA
RUN curl -L https://slicer-packages.kitware.com/api/v1/file/hashsum/SHA512/e77abd5e8d7b59088da65ae6b8b872b4aa5ead6acb47e5d4e3231db7a76ca41b6f8df4a9ac8352f1a6c5c46b932099fbb65ed7cbc98f36690b5379c7b4a478c3/download > /33996-SlicerSOFA-gitd61d908-g++-64bits-Qt5.15-Release.tar.gz

#Copy QuantitativeReporting Slicer Extension
COPY packages/30822-linux-amd64-QuantitativeReporting-gitd4892cf-2022-04-08.tar.gz /

# Make Extensions directory and install dependencies
#TODO: This apparently still does not pull some dependencies for the QuantitativeReporting Slicer Exension
#      A workaround is to launch Slicer inside the container and install the QuantitativeReporting there
COPY scripts/slicer_install_dependencies.py /
RUN xvfb-run --auto-servernum --server-args='-screen 0 1024x768x24' \
    /opt/Slicer-5.9.0-2025-10-13-linux-amd64/Slicer --no-main-window --launcher-no-splash --python-script /slicer_install_dependencies.py
RUN rm /slicer_install_dependencies.py

RUN xvfb-run --auto-servernum --server-args='-screen 0 1024x768x24' \
    /opt/Slicer-5.9.0-2025-10-13-linux-amd64/Slicer --launch PythonSlicer -m pip install pyacvd==0.3.1

# Change permissions of /opt/Slicer to make it writable for the user running the container
RUN chmod -R ugo+w /opt/Slicer-*

RUN curl -L https://github.com/QIICR/dcmqi/releases/download/v1.3.4/dcmqi-1.3.4-linux.tar.gz | tar xz -C /opt

# Download dataset manifest
RUN mkdir -p /data && \
    cd /data && \
    curl -LO https://www.cancerimagingarchive.net/wp-content/uploads/Colorectal-Liver-Metastases-November-2022-manifest.tcia

COPY run.sh /
RUN chmod ug+x /run.sh

COPY scripts/TCIA_data_augmentation.py /

ENTRYPOINT ["/run.sh"]
