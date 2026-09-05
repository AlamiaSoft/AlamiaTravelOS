FROM odoo:19.0

USER root

# Install system dependencies required by Odoo/custom Python packages
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    python3-dev \
    libssl-dev \
    libffi-dev \
    libxml2-dev \
    libxslt1-dev \
    zlib1g-dev \
    git \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install Python libraries for Odoo travel/ERP customizations
RUN pip3 install --no-cache-dir --break-system-packages \
    phonenumbers \
    xlsxwriter \
    openpyxl \
    pandas \
    requests \
    pyjwt \
    cryptography \
    paramiko \
    xmltodict \
    qrcode \
    "authlib>=1.6.12,<1.7.0" \
    defusedxml \
    packaging

# Copy Odoo configuration
COPY config/odoo/odoo.conf /etc/odoo/odoo.conf

# Copy custom addons into the image
COPY custom-addons/ /mnt/extra-addons/

# Copy third-party addons into the image, if present
COPY third-party-addons/ /mnt/third-party-addons/

# Ensure Odoo owns the application files
RUN chown -R odoo:odoo \
    /etc/odoo/odoo.conf \
    /mnt/extra-addons \
    /mnt/third-party-addons

USER odoo
