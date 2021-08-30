import apache_beam as beam
import logging
from apache_beam.options.pipeline_options import PipelineOptions, GoogleCloudOptions, StandardOptions, SetupOptions

class TemplateOptions(PipelineOptions):
    @classmethod
    def _add_argparse_args(cls, parser):
        parser.add_value_provider_argument("--input",
                            type=str,
                            help='Input csv to process',
                            dest='input',
                            required=False)
        parser.add_value_provider_argument("--output",
                            type=str,
                            help='Output path to write to in bq or gcs',
                            dest='output',
                            required=False)
        parser.add_value_provider_argument("--mode",
                            type=str,
                            help='mode either `bq` or `gcs`',
                            default='gcs',
                            dest='mode',
                            required=False)

def run():
    options = PipelineOptions()
    options.view_as(StandardOptions).runner = 'DataFlowRunner'
    options.view_as(GoogleCloudOptions).project = 'bigquery-cp-project'
    options.view_as(GoogleCloudOptions).temp_location = 'gs://beam-stg/temp'
    options.view_as(GoogleCloudOptions).region = 'europe-west2'
    options.view_as(GoogleCloudOptions).job_name = 'flex-load-test'
    user_args = options.view_as(TemplateOptions)

    with beam.Pipeline(options=options) as p:
        read_data = (p | 'read_csv' >> beam.io.ReadFromText(file_pattern=user_args.input, skip_header_lines=0))
        if user_args.mode == 'gcs':
            write_gcs = (read_data | 'write_storage' >> beam.io.WriteToText(file_path_prefix=f"gs://cp-csv-bucket/{user_args.output}", file_name_suffix='.txt'))
        else:
            formatted_row = (read_data | 'format_as_row' >> beam.Map(lambda x: {"id": 1, "row_content": str(x)}))
            write_bq = (formatted_row | 'write_bq' >> beam.io.WriteToBigQuery(f"bigquery-cp-project:beam_results.{user_args.output}",schema='id:INTEGER,row:STRING',create_disposition='CREATE_IF_NEEDED', write_disposition='WRITE_EMPTY'))


if __name__ == '__main__':
    logging.getLogger().setLevel(logging.INFO)
    run()