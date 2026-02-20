#!/usr/bin/env python3
"""
Generate a multi-sample IGV session XML file excluding BAM tracks.
"""

import argparse
import xml.etree.ElementTree as ET
from xml.dom import minidom
import os 

def create_multi_sample_igv_session(
    sample_ids,
    locus,
    genome="hg38",
    base_url="http://localhost:8080",
    methylation_type="count"
):
    """
    Create an IGV session XML for multiple individuals.
    """
    # Create root Session element
    session = ET.Element("Session", {
        "genome": genome,
        "locus": locus,
        "version": "8"
    })
    
    # Create Resources section
    resources = ET.SubElement(session, "Resources")
    
    # Create DataPanel for all methylation tracks
    data_panel = ET.SubElement(session, "Panel", {"name": "DataPanel", "height": "400"})
    
    # Create FeaturePanel for all haplotype blocks
    feature_panel = ET.SubElement(session, "Panel", {"name": "FeaturePanel", "height": "200"})

    # Add VCF resources and tracks
    vcf_path = f"{base_url}/vcfs/CEPH-1463.joint.GRCh38.deepvariant.glnexus.phased.vcf.gz"
    vcf_index = f"{vcf_path}.tbi"
    ET.SubElement(resources, "Resource", {"index": vcf_index, "path": vcf_path, "type": "vcf"})

    ET.SubElement(feature_panel, "Track", {
        "attributeKey": "joint_vcf",
        "clazz": "org.broad.igv.variant.VariantTrack",
        "displayMode": "COLLAPSED",
        "fontSize": "10",
        "id": vcf_path,
        "name": "All variants",
        "visible": "true"
    })

    vcf_iht_path = f"{base_url}/vcfs-iht-phased/CEPH1463.GRCh38.pass.sorted.vcf.gz"
    vcf_iht_index = f"{vcf_iht_path}.tbi"
    ET.SubElement(resources, "Resource", {"index": vcf_iht_index, "path": vcf_iht_path, "type": "vcf"})

    ET.SubElement(feature_panel, "Track", {
        "attributeKey": "joint_vcf_iht_phased",
        "clazz": "org.broad.igv.variant.VariantTrack",
        "fontSize": "10",
        "id": vcf_iht_path,
        "name": "Phased variants (PAT|MAT)",
        "visible": "true"
    })

    for sample_id in sample_ids:
        # 1. Add Resources (BigWig and BED)
        # Methylation BigWigs
        for parent in ["pat", "mat"]:
            path = f"{base_url}/founder-phased/{sample_id}.dna-methylation.founder-phased.{parent}.{methylation_type}.{genome}.bw"
            ET.SubElement(resources, "Resource", {"path": path, "type": "bw"})
            
            # 2. Add Methylation Tracks to DataPanel
            ET.SubElement(data_panel, "Track", {
                "attributeKey": f"{sample_id}_{parent}_meth",
                "autoScale": "false",
                "clazz": "org.broad.igv.track.DataSourceTrack",
                "fontSize": "10",
                "id": path,
                "name": f"{sample_id} {parent.upper()} Methylation",
                "renderer": "BAR_CHART",
                "visible": "true",
                "windowFunction": "mean"
            }).append(ET.Element("DataRange", {
                "baseline": "0.0", "drawBaseline": "true", "maximum": "1.0", "minimum": "0.0", "type": "LINEAR"
            }))

        # Haplotype BEDs
        for parent in ["paternal", "maternal"]:
            bed_path = f"{base_url}/founder-phased/{sample_id}.hap-map-blocks.{parent}.sorted.bed.gz"
            index_path = f"{bed_path}.tbi"
            ET.SubElement(resources, "Resource", {"index": index_path, "path": bed_path, "type": "bed"})
            
            # 3. Add Haplotype Tracks to FeaturePanel
            ET.SubElement(feature_panel, "Track", {
                "attributeKey": f"{sample_id}_{parent}_blocks",
                "clazz": "org.broad.igv.track.FeatureTrack",
                "featureVisibilityWindow": "2147483647",
                "fontSize": "10",
                "id": bed_path,
                "name": f"{sample_id} {parent.upper()[:3]} Blocks",
                "visible": "true"
            })

    # Add Standard Reference Tracks to FeaturePanel
    ET.SubElement(feature_panel, "Track", {
        "clazz": "org.broad.igv.track.SequenceTrack",
        "fontSize": "10",
        "id": "Reference sequence",
        "name": "Reference sequence",
        "visible": "true"
    })

    # Layout for two panels
    ET.SubElement(session, "PanelLayout", {"dividerFractions": "0.60"})
    
    # Pretty print
    xml_str = ET.tostring(session, encoding='unicode')
    dom = minidom.parseString(xml_str)
    return '\n'.join([line for line in dom.toprettyxml(indent="    ").split('\n') if line.strip()])

def main():
    parser = argparse.ArgumentParser(description="Generate a multi-sample IGV session.")
    
    # Changed 'nillable=False' to 'required=True'
    parser.add_argument(
        "--samples", 
        required=True, 
        help="Comma-separated list of sample IDs (e.g., sample1,sample2)"
    )
    
    parser.add_argument(
        "--locus", 
        required=True, 
        help="Genomic locus (e.g., chr14:100826000-100827000)"
    )
    
    parser.add_argument(
        "--out", 
        default="multi_sample_session.xml", 
        help="Output filename in the igv-sessions directory"
    )
    
    args = parser.parse_args()
    
    # Split the comma-separated string into a list
    sample_list = [s.strip() for s in args.samples.split(",")]
    
    # Generate the session
    xml_content = create_multi_sample_igv_session(sample_list, args.locus)
    
    # Create directory to store sessions 
    sessions_dir = 'igv-sessions'
    os.makedirs(sessions_dir, exist_ok=True)

    # Save the file
    output_path = os.path.join(sessions_dir, args.out)
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(xml_content)
    
    print(f"Multi-sample IGV session created: {output_path}")
    
if __name__ == "__main__":
    main()