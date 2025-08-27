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

#Download and install 3D Slicer 5.9.0
RUN curl -L https://download.slicer.org/bitstream/685f7312a2a452fc449ea770 | tar xz -C /opt

#Download Slicer-SOFA
RUN curl -L https://slicer-packages.kitware.com/api/v1/item/68610041a2a452fc449f2adf/download > 33727-linux-amd64-SlicerSOFA-git63eb08b-2025-06-27.tar.gz

#Copy QuantitativeReporting Slicer Extension
COPY packages/30822-linux-amd64-QuantitativeReporting-gitd4892cf-2022-04-08.tar.gz /

# Make Extensions directory and install dependencies
#TODO: This apparently still does not pull some dependencies for the QuantitativeReporting Slicer Exension
#      A workaround is to launch Slicer inside the container and install the QuantitativeReporting there
COPY scripts/slicer_install_dependencies.py /
RUN xvfb-run --auto-servernum --server-args='-screen 0 1024x768x24' \
    /opt/Slicer-5.9.0-2025-06-27-linux-amd64/Slicer --no-main-window --launcher-no-splash --python-script /slicer_install_dependencies.py
RUN rm /slicer_install_dependencies.py

# Change permissions of /opt/Slicer to make it writable for the user running the container
RUN chmod -R ugo+w /opt/Slicer-*

RUN curl -L https://github.com/QIICR/dcmqi/releases/download/v1.3.4/dcmqi-1.3.4-linux.tar.gz | tar xz -C /opt

# Download dataset manifest
RUN mkdir -p /data && \
    cd /data && \
    curl -LO https://www.cancerimagingarchive.net/wp-content/uploads/Colorectal-Liver-Metastases-November-2022-manifest.tcia

COPY run.sh /
RUN chmod ug+x /run.sh

ENTRYPOINT ["/run.sh"]
