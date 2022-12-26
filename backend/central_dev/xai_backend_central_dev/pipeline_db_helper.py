from tinydb import TinyDB, Query


class PipelineDB():

    def __init__(self, pipeline_db_path: str) -> None:

        self.db = TinyDB(pipeline_db_path)
        self.pipeline_tb = self.db.table('pipeline', cache_size=0)

        self.xai_task_sheet_tb = self.db.table('xai_task_sheet', cache_size=0)
        self.evaluation_task_sheet_tb = self.db.table(
            'evaluation_task_sheet', cache_size=0)
        # TODO: predictionn task
        self.prediction_task_sheet_tb = self.db.table(
            'prediction_task_sheet', cache_size=0)
