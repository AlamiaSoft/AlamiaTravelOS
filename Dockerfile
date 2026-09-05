FROM odoo:19.0

USER root

# Install system dependencies if required for compiling native python packages
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

# Install Python libraries for Odoo travel/ERP customizations + MCP Server dependencies
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

# Copy custom configuration and addons into image
COPY config/odoo.conf /etc/odoo/odoo.conf
COPY custom_addons /mnt/extra-addons
COPY third_party_addons /mnt/third-party-addons

RUN chown -R odoo:odoo /etc/odoo /mnt/extra-addons /mnt/third-party-addons

# Switch back to the unprivileged odoo user
USER odoo
